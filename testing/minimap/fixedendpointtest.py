import numpy as np
from filterpy.kalman import ExtendedKalmanFilter
import csv
import time

def normalize_quat(q):
    return q / np.linalg.norm(q)

def quat_to_rot_mat(q):
    w,x,y,z = q
    return np.array([
        [1-2*(y*y+z*z),   2*(x*y - z*w),   2*(x*z + y*w)],
        [2*(x*y + z*w),   1-2*(x*x+z*z),   2*(y*z - x*w)],
        [2*(x*z - y*w),   2*(y*z + x*w),   1-2*(x*x+y*y)]
    ])

def acc_mag_prediction(q, g_ref=np.array([0,0,1]), m_ref=np.array([1,0,0])):
    R  = quat_to_rot_mat(q)
    gb = R.T @ g_ref
    mb = R.T @ (m_ref/np.linalg.norm(m_ref))
    return np.hstack((gb, mb))

def H_jacobian(x):
    q = x[0:4]
    eps = 1e-6
    H = np.zeros((6, x.shape[0]))
    for i in range(4):
        dq = np.zeros(4); dq[i] = eps
        zp = acc_mag_prediction(normalize_quat(q + dq))
        zm = acc_mag_prediction(normalize_quat(q - dq))
        H[:, i] = (zp - zm)/(2*eps)
    return H

def tilt_compensated_heading(mag, q):
    """
    Compute measured heading by first rotating mag into nav frame
    (so gravity tilt is removed) and then atan2(E,N).
    """
    R = quat_to_rot_mat(q)
    # rotation body→nav:
    m_nav = R @ mag
    # heading = atan2(East, North)
    return np.arctan2(m_nav[1], m_nav[0])

class OrientationBiasEKF:
    def __init__(self):
        # [q0,q1,q2,q3, bgx,bgy,bgz]
        self.ekf = ExtendedKalmanFilter(dim_x=7, dim_z=6)
        self.ekf.x = np.hstack((np.array([1.,0.,0.,0.]), np.zeros(3)))
        self.ekf.P = np.eye(7)*0.01
        Q = np.eye(7)*1e-5
        Q[4:,4:] *= 1e-4
        self.ekf.Q = Q
        self.R_accmag = np.eye(6)*1e-4
        self.R_yaw    = np.array([[1e-3]])   # tighter yaw correction

    def predict(self, gyro, dt):
        gb = self.ekf.x[4:7]
        wx,wy,wz = gyro - gb
        Omega = np.array([
            [0,   -wx, -wy, -wz],
            [wx,   0,   wz, -wy],
            [wy,  -wz,  0,   wx],
            [wz,   wy, -wx,  0  ]
        ])
        F = np.eye(7)
        F[0:4,0:4] = np.eye(4) + 0.5*dt*Omega
        self.ekf.F = F
        self.ekf.predict()

    def update(self, accel, mag):
        # 1) full accel+mag update
        if accel == 0:
            accel = 1e-6
        a_norm = accel/np.linalg.norm(accel)
        m_norm = mag/np.linalg.norm(mag)
        z_am = np.hstack((a_norm, m_norm))

        self.ekf.R = self.R_accmag
        self.ekf.update(
            z_am,
            HJacobian=lambda x: H_jacobian(x),
            Hx=lambda x: acc_mag_prediction(x[0:4])
        )
        # re‐normalize quaternion
        self.ekf.x[0:4] = normalize_quat(self.ekf.x[0:4])

        # 2) yaw‐only compass update
        q = self.ekf.x[0:4]
        yaw_meas = tilt_compensated_heading(mag, q)

        # define h_yaw and H_yaw via numeric jacobian on the full state:
        def h_yaw(x):
            return np.array([ tilt_compensated_heading(mag, x[0:4]) ])

        def H_yaw(x):
            eps = 1e-6
            Hh = np.zeros((1,7))
            for i in range(4):
                dx = np.zeros(7); dx[i]=eps
                hp = tilt_compensated_heading(mag, normalize_quat(x[0:4]+dx[0:4]))
                hm = tilt_compensated_heading(mag, normalize_quat(x[0:4]-dx[0:4]))
                Hh[0,i] = (hp - hm)/(2*eps)
            return Hh

        self.ekf.R = self.R_yaw
        self.ekf.update(
            np.array([yaw_meas]),
            HJacobian=H_yaw,
            Hx=h_yaw
        )
        # normalize again
        self.ekf.x[0:4] = normalize_quat(self.ekf.x[0:4])

        return self.ekf.x[0:4]

# ——— Rod tracker: orientation + 1D insertion depth with variable dt ———
class RodTracker:
    def __init__(self, L):
        self.L = L
        self.orient_filter = OrientationBiasEKF()
        self.s = 0.0               # axial displacement from start
        self.v_axial = 0.0         # axial velocity
        self.prev_timestamp = None

    def update(self, gyro, accel, mag, timestamp):
        # 1) compute dt
        if self.prev_timestamp is None:
            dt = 0.0
        else:
            dt = timestamp - self.prev_timestamp
        self.prev_timestamp = timestamp

        # 2) orientation EKF
        self.orient_filter.predict(gyro, dt)
        q = self.orient_filter.update(accel, mag)

        # 3) rotate accel nav→body & extract axial component
        #    (body Z points along rod axis)
        accel_nav  = quat_to_rot_mat(q) @ accel
        # bring back into body frame:
        a_body     = quat_to_rot_mat(q).T @ accel_nav
        a_axial    = a_body[2]    # axial accel

        # 4) integrate displacement along rod
        self.s += self.v_axial * dt + 0.5 * a_axial * dt**2

        # 5) ZUPT: if stationary, reset velocity
        acc_dir = accel / np.linalg.norm(accel)
        if (np.linalg.norm(acc_dir - np.array([0,0,1])) < 0.03
            and np.linalg.norm(gyro) < 0.01):
            self.v_axial = 0.0
        else:
            self.v_axial += a_axial * dt

        # 6) compute 3D tip position
        R       = quat_to_rot_mat(q)
        tip_pos = R @ np.array([0, 0, self.L + self.s])
        return tip_pos, q, self.s

if __name__ == "__main__":
    def read_imu_data(csv_path):
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = float(row['Timestamp'])
                accel = np.array([float(row['Accel_X']), float(row['Accel_Y']), float(row['Accel_Z'])])
                gyro  = np.array([float(row['Gyro_X']),  float(row['Gyro_Y']),  float(row['Gyro_Z'])])
                mag   = np.array([float(row['Mag_X']),   float(row['Mag_Y']),   float(row['Mag_Z'])])
                yield ts, gyro, accel, mag

    L = 0.13 # rod length [m]
    tracker = RodTracker(L)
    for ts, gyro, accel, mag in read_imu_data('circle_in_one_plane.csv'):
        tip, quat, depth = tracker.update(gyro, accel, mag, ts)
        x, y, z = tip
        print(f"Time {ts:.3f}s | Tip -> X:{x:.3f} m, Y:{y:.3f} m, Z:{z:.3f} m; Depth:{depth:.3f} m; Quat:{quat.round(4)}")
        time.sleep(0.01)