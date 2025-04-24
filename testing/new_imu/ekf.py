import numpy as np
import pandas as pd
from ahrs.filters import EKF

def quaternion_to_rotation_matrix(q):
    w, x, y, z = q
    return np.array([
        [1 - 2*(y*y + z*z),     2*(x*y - w*z),     2*(x*z + w*y)],
        [    2*(x*y + w*z), 1 - 2*(x*x + z*z),     2*(y*z - w*x)],
        [    2*(x*z - w*y),     2*(y*z + w*x), 1 - 2*(x*x + y*y)]
    ])

# ——— LOAD DATA ———
df = pd.read_csv('50cm_trial1_extracted.csv')
n  = len(df)

Q = np.zeros((n, 4))
V = np.zeros((n, 3))
P = np.zeros((n, 3))

# ——— INIT EKF ———
ekf = EKF()
ekf.sampleperiod = df.at[1, 'Timestamp'] - df.at[0, 'Timestamp']  # initial guess
Q[0] = [1.0, 0.0, 0.0, 0.0]

for i in range(1, n):
    # Δt
    dt = df.at[i, 'Timestamp'] - df.at[i-1, 'Timestamp']
    ekf.sampleperiod = dt

    gyr = df.loc[i, ['Gyro_X','Gyro_Y','Gyro_Z']].values
    acc = df.loc[i, ['Accel_X','Accel_Y','Accel_Z']].values
    mag = df.loc[i, ['Mag_X','Mag_Y','Mag_Z']].values

    # —— Replace updateMARG with update() —— 
    # EKF.update will use mag if you pass it, otherwise falls back to IMU-only
    Q[i] = ekf.update(Q[i-1], gyr=gyr, acc=acc, mag=mag)

    # Rotate into world, integrate as before
    Rwb       = quaternion_to_rotation_matrix(Q[i])
    acc_world = Rwb.dot(acc)

    V[i] = V[i-1] + acc_world * dt
    P[i] = P[i-1] + V[i] * dt

print("Final displacement (m):", P[-1])
