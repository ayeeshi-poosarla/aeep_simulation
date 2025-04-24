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

def acc_mag_prediction(q, g_ref=np.array([0,0,1]), m_ref=np.array([1,0,0])):
    """
    Predicted body-frame gravity & magnetic field (unit vectors),
    given orientation q.
    """
    R = quat_to_rot_mat(q)
    g_b = R.T @ g_ref
    m_b = R.T @ (m_ref / np.linalg.norm(m_ref))
    return np.hstack((g_b, m_b))

def H_jacobian(x):
    """
    Numeric Jacobian of h(x)=acc_mag_prediction around state x (4×1 quaternion).
    Returns 6×4 matrix.
    """
    eps = 1e-6
    H = np.zeros((6, 4))
    for i in range(4):
        dq = np.zeros(4); dq[i] = eps
        zp = acc_mag_prediction(normalize_quat(x + dq))
        zm = acc_mag_prediction(normalize_quat(x - dq))
        H[:, i] = (zp - zm) / (2 * eps)
    return H

# ——— Extended Kalman Filter for orientation ———

class OrientationEKF:
    def __init__(self, dt):
        self.dt = dt
        self.ekf = ExtendedKalmanFilter(dim_x=4, dim_z=6)
        # initial state = identity quaternion
        self.ekf.x = np.array([1.0, 0.0, 0.0, 0.0])
        # small initial uncertainty
        self.ekf.P = np.eye(4) * 0.01
        # process noise (tune as needed)
        self.ekf.Q = np.eye(4) * 1e-4
        # measurement noise (acc + mag)
        self.ekf.R = np.eye(6) * 1e-2

    def predict(self, gyro):
        """
        gyro: np.array([ωx, ωy, ωz]) in rad/s.
        Uses q̇ = ½·Ω(ω)·q to build F ≈ I + ½·dt·Ω.
        """
        wx, wy, wz = gyro
        Ω = np.array([
            [ 0,   -wx, -wy, -wz],
            [ wx,   0,   wz, -wy],
            [ wy,  -wz,  0,   wx],
            [ wz,   wy, -wx,  0  ]
        ])
        self.ekf.F = np.eye(4) + 0.5 * self.dt * Ω
        self.ekf.predict()

    def update(self, accel, mag):
        """
        accel: np.array([ax,ay,az]) in m/s²,
        mag:   np.array([mx,my,mz]) in any units.
        We normalize both for use as direction measurements.
        """
        a_norm = accel / np.linalg.norm(accel)
        m_norm = mag   / np.linalg.norm(mag)
        z = np.hstack((a_norm, m_norm))
        self.ekf.update(
            z,
            HJacobian=lambda x: H_jacobian(x),
            Hx=lambda x: acc_mag_prediction(x)
        )
        self.ekf.x = normalize_quat(self.ekf.x)
        return self.ekf.x

# ——— Rod tracker combining orientation + simple dead-reckoning ———

class RodTracker:
    def __init__(self, dt, L):
        self.dt = dt
        self.L = L
        self.orient_filter = OrientationEKF(dt)
        # for dead-reckoning the IMU position
        self.velocity = np.zeros(3)
        self.position = np.zeros(3)
        self.displacement = 0

    def update(self, gyro, accel, mag):
        # 1) orientation EKF
        self.orient_filter.predict(gyro)
        q = self.orient_filter.update(accel, mag)

        # 2) turn body accel into nav frame & subtract gravity
        R = quat_to_rot_mat(q)
        a_nav = R @ accel 

        # 3) simple integration (will drift!)
        self.velocity += a_nav * self.dt
        self.position += self.velocity * self.dt + 0.5 * a_nav * self.dt**2

        # 4) compute end-of-rod pose
        #    position of rod tip in nav frame:
        rod_tip = self.position + R @ np.array([0, 0, self.L])
        #    orientation of rod = q
        return rod_tip, q

# ——— Example usage ———

if __name__ == "__main__":
    # your IMU read function
    
    
    def read_imu_data(csv_path):
        """
        Generator that yields (gyro, accel, mag) tuples from a CSV with
        columns: Timestamp,Accel_X,Accel_Y,Accel_Z,Gyro_X,Gyro_Y,Gyro_Z,Mag_X,Mag_Y,Mag_Z
        """
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # parse into numpy arrays
                accel = np.array([
                    float(row['Accel_X']),
                    float(row['Accel_Y']),
                    float(row['Accel_Z'])
                ])
                gyro = np.array([
                    float(row['Gyro_X']),
                    float(row['Gyro_Y']),
                    float(row['Gyro_Z'])
                ])
                mag = np.array([
                    float(row['Mag_X']),
                    float(row['Mag_Y']),
                    float(row['Mag_Z'])
                ])
                yield gyro, accel, mag

    dt = 0.10        #
    L  = 0         # rod length = 15 cm
    tracker = RodTracker(dt, L)
    csv_path = '30cm_trial1_extracted.csv'
    imu_stream = read_imu_data(csv_path)
    for gyro, accel, mag in read_imu_data(csv_path):
        rod_tip, q = tracker.update(gyro, accel, mag)
        print(f"Rod tip position: {rod_tip}, Quaternion: {q}")
        time.sleep(dt)
