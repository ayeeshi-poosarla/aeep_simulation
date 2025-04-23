import numpy as np
import csv
import time
from filterpy.kalman import ExtendedKalmanFilter

# ——— quaternion utilities ———

def normalize_quat(q):
    return q / np.linalg.norm(q)

def quat_to_rot_mat(q):
    """Convert unit quaternion [w, x, y, z] to 3×3 rotation matrix."""
    w, x, y, z = q
    return np.array([
        [1 - 2*(y*y + z*z),   2*(x*y - z*w),     2*(x*z + y*w)],
        [2*(x*y + z*w),       1 - 2*(x*x + z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w),       2*(y*z + x*w),     1 - 2*(x*x + y*y)]
    ])

# ——— measurement model & Jacobian for EKF ———

def acc_mag_prediction(q, g_ref=np.array([0,0,1]), m_ref=np.array([1,0,0])):
    """
    Predicts body-frame gravity & magnetic vectors given orientation quaternion q.
    Returns concatenated 6×1 vector [g_b; m_b].
    """
    R = quat_to_rot_mat(q)
    g_b = R.T @ g_ref
    m_b = R.T @ (m_ref / np.linalg.norm(m_ref))
    return np.hstack((g_b, m_b))

def H_jacobian(x):
    """
    Numerical Jacobian of acc_mag_prediction w.r.t the quaternion part of state x.
    x is 7×1: [q; bias]. We return a 6×7 matrix, with zeros for bias derivatives.
    """
    q = x[0:4]
    eps = 1e-6
    H = np.zeros((6, 7))
    for i in range(4):
        dq = np.zeros(4);
        dq[i] = eps
        zp = acc_mag_prediction(normalize_quat(q + dq))
        zm = acc_mag_prediction(normalize_quat(q - dq))
        H[:, i] = (zp - zm) / (2 * eps)
    # columns 4-6 for biases remain zero
    return H

# ——— Extended Kalman Filter for orientation + gyro bias ———
class OrientationBiasEKF:
    def __init__(self, dt):
        self.dt = dt
        # state: [qw, qx, qy, qz, bgx, bgy, bgz]
        self.ekf = ExtendedKalmanFilter(dim_x=7, dim_z=6)
        self.ekf.x = np.hstack((np.array([1.0,0.0,0.0,0.0]), np.zeros(3)))
        self.ekf.P = np.eye(7) * 0.01
        # process noise: small for quaternion, moderate for bias random walk
        Q = np.eye(7) * 1e-5
        Q[4:,4:] *= 1e-4
        self.ekf.Q = Q
        self.ekf.R = np.eye(6) * 1e-2

    def predict(self, gyro):
        # subtract estimated gyro bias
        gyro_corr = gyro - self.ekf.x[4:7]
        wx, wy, wz = gyro_corr
        # Omega for quaternion kinematics
        Omega = np.array([
            [ 0,   -wx, -wy, -wz],
            [ wx,   0,   wz, -wy],
            [ wy,  -wz,  0,   wx],
            [ wz,   wy, -wx,  0  ]
        ])
        # state transition F
        F = np.eye(7)
        F[0:4,0:4] = np.eye(4) + 0.5 * self.dt * Omega
        F[0:4,4:7] = np.zeros((4,3))  # no direct coupling
        self.ekf.F = F
        self.ekf.predict()

    def update(self, accel, mag):
        # normalize measurements
        a_norm = accel / np.linalg.norm(accel)
        m_norm = mag   / np.linalg.norm(mag)
        z = np.hstack((a_norm, m_norm))
        self.ekf.update(
            z,
            HJacobian=lambda x: H_jacobian(x),
            Hx=lambda x: acc_mag_prediction(x[0:4])
        )
        # renormalize quaternion
        self.ekf.x[0:4] = normalize_quat(self.ekf.x[0:4])
        return self.ekf.x[0:4]

# ——— Rod tracker: orientation + 1D insertion depth ———
class RodTracker:
    def __init__(self, dt, L):
        self.dt = dt
        self.L = L                  # base insertion offset
        self.orient_filter = OrientationBiasEKF(dt)
        self.s = 0.0                # insertion depth
        self.v_axial = 0.0          # axial velocity

    def update(self, gyro, accel, mag):
        # orientation + bias estimation
        self.orient_filter.predict(gyro)
        q = self.orient_filter.update(accel, mag)
        R = quat_to_rot_mat(q)

        # remove gravity in nav frame
        accel_nav = R @ accel
        a_nav = accel_nav
        # project to body Z-axis
        a_body = R.T @ a_nav
        a_axial = a_body[2]

        # ZUPT: reset velocity if stationary
        acc_dir = accel / np.linalg.norm(accel)
        if np.linalg.norm(acc_dir - np.array([0,0,1])) < 0.03 and np.linalg.norm(gyro) < 0.01:
            self.v_axial = 0.0
        else:
            self.v_axial += a_axial * self.dt

        # integrate depth
        self.s += self.v_axial * self.dt + 0.5 * a_axial * self.dt**2

        # compute tip in nav frame
        tip_pos = R @ np.array([0, 0, self.L + self.s])
        return tip_pos, q, self.s

# ——— Example usage reading CSV ———
if __name__ == "__main__":
    def read_imu_data(csv_path):
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                accel = np.array([float(row['Accel_X']), float(row['Accel_Y']), float(row['Accel_Z'])])
                gyro  = np.array([float(row['Gyro_X']),  float(row['Gyro_Y']),  float(row['Gyro_Z'])])
                mag   = np.array([float(row['Mag_X']),   float(row['Mag_Y']),   float(row['Mag_Z'])])
                yield gyro, accel, mag

    dt = 0.1
    L  = 0.15
    tracker = RodTracker(dt, L)
    for gyro, accel, mag in read_imu_data('testing/new_imu/Trial3_Y_extracted.csv'):
        tip, quat, depth = tracker.update(gyro, accel, mag)
        print(f"Tip: {tip.round(3)} m, Depth: {depth:.3f} m, Orientation: {quat.round(4)}")
        time.sleep(dt)
