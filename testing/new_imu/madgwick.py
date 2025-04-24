import numpy as np
import pandas as pd
from ahrs.filters import Madgwick

def quaternion_to_rotation_matrix(q):
    w, x, y, z = q
    return np.array([
        [1 - 2*(y*y + z*z),   2*(x*y - w*z),   2*(x*z + w*y)],
        [  2*(x*y + w*z),   1 - 2*(x*x + z*z), 2*(y*z - w*x)],
        [  2*(x*z - w*y),     2*(y*z + w*x), 1 - 2*(x*x + y*y)]
    ])

# Load your data
df = pd.read_csv('30cm_trial2_extracted.csv')
n  = len(df)

Q = np.zeros((n, 4))
V = np.zeros((n, 3))
P = np.zeros((n, 3))

# Initialize Madgwick filter
madgwick       = Madgwick()        # you can also pass beta=… or an initial sampleperiod here
Q[0]           = [1.0, 0.0, 0.0, 0.0]

for i in range(1, n):
    # Compute Δt
    dt = df.at[i, 'Timestamp'] - df.at[i-1, 'Timestamp']

    # Tell the filter what your sample period is
    madgwick.sampleperiod = dt

    # Grab your sensors
    acc = df.loc[i, ['Accel_X','Accel_Y','Accel_Z']].values
    gyr = df.loc[i, ['Gyro_X','Gyro_Y','Gyro_Z']].values
    #mag = df.loc[i, ['Mag_X','Mag_Y','Mag_Z']].values
    mag = np.zeros(3)

    # Update orientation (no dt argument here!)
    Q[i] = madgwick.updateMARG(Q[i-1], gyr=gyr, acc=acc, mag=mag)

    # Rotate accel into world frame
    Rwb       = quaternion_to_rotation_matrix(Q[i])
    acc_world = Rwb.dot(acc)

    # Integrate velocity & position
    V[i] = V[i-1] + acc_world * dt
    P[i] = P[i-1] + V[i] * dt

print("Final displacement (m):", P[-1])
