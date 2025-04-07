import numpy as np
import pandas as pd

class MadgwickFilter:
    def __init__(self, sample_period, beta=0.1):
        """
        Initializes the Madgwick filter.
        
        Parameters:
        -----------
        sample_period : float
            The sample period (in seconds) between measurements.
        beta : float
            The filter gain; higher beta gives more weight to the correction.
        """
        self.sample_period = sample_period
        self.beta = beta
        # Initialize quaternion: [q0, q1, q2, q3]
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
    
    def update(self, gyro, accel, mag):
        """
        Update the filter with new sensor measurements.
        
        Parameters:
        -----------
        gyro : array-like, shape (3,)
            Gyroscope measurements (rad/s) as [gx, gy, gz].
        accel : array-like, shape (3,)
            Accelerometer measurements (in g or m/s^2, if gravity is present).
        mag : array-like, shape (3,)
            Magnetometer measurements.
            
        Returns:
        --------
        q : ndarray, shape (4,)
            The updated orientation quaternion.
        """
        q1, q2, q3, q4 = self.q

        # Normalize accelerometer measurement
        if np.linalg.norm(accel) == 0:
            return self.q  # avoid division by zero
        accel = accel / np.linalg.norm(accel)

        # Normalize magnetometer measurement
        if np.linalg.norm(mag) == 0:
            return self.q
        mag = mag / np.linalg.norm(mag)

        # Auxiliary variables to avoid repeated arithmetic
        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _2q4 = 2.0 * q4
        _4q1 = 4.0 * q1
        _4q2 = 4.0 * q2
        _4q3 = 4.0 * q3
        _8q2 = 8.0 * q2
        _8q3 = 8.0 * q3
        q1q1 = q1 * q1
        q2q2 = q2 * q2
        q3q3 = q3 * q3
        q4q4 = q4 * q4
        q2q4 = q2 * q4

        # Reference direction of Earth's magnetic field
        hx = mag[0] * (q1q1 + q2q2 - q3q3 - q4q4) + 2.0 * mag[1] * (q2 * q3 - q1 * q4) + 2.0 * mag[2] * (q2 * q4 + q1 * q3)
        hy = 2.0 * mag[0] * (q2 * q3 + q1 * q4) + mag[1] * (q1q1 - q2q2 + q3q3 - q4q4) + 2.0 * mag[2] * (q3 * q4 - q1 * q2)
        _2bx = np.sqrt(hx * hx + hy * hy)
        _2bz = 2.0 * mag[0] * (q2 * q4 - q1 * q3) + 2.0 * mag[1] * (q3 * q4 + q1 * q2) + mag[2] * (q1q1 - q2q2 - q3q3 + q4q4)

        # Gradient descent algorithm corrective step
        f1 = _2q2 * q4 - _2q1 * q3 - accel[0]
        f2 = _2q1 * q2 + _2q3 * q4 - accel[1]
        f3 = 1.0 - _2q2 * q2 - _2q3 * q3 - accel[2]
        # Similarly, include terms that incorporate the magnetic field;
        # for brevity, we combine them into s1, s2, s3, s4 below.
        s1 = -_2q3 * (2.0 * q2q4 - _2q1 * q3 - accel[0]) + _2q2 * (2.0 * q1 * q2 + _2q3 * q4 - accel[1])
        s2 = _2q4 * (2.0 * q2q4 - _2q1 * q3 - accel[0]) + _2q1 * (2.0 * q1 * q2 + _2q3 * q4 - accel[1]) - 4.0 * q2 * (1.0 - 2.0 * q2q2 - 2.0 * q3q3 - accel[2])
        s3 = -_2q1 * (2.0 * q2q4 - _2q1 * q3 - accel[0]) + _2q4 * (2.0 * q1 * q2 + _2q3 * q4 - accel[1]) - 4.0 * q3 * (1.0 - 2.0 * q2q2 - 2.0 * q3q3 - accel[2])
        s4 = _2q2 * (2.0 * q2q4 - _2q1 * q3 - accel[0]) + _2q3 * (2.0 * q1 * q2 + _2q3 * q4 - accel[1])
        norm_s = np.linalg.norm([s1, s2, s3, s4])
        if norm_s == 0:
            norm_s = 1
        s1, s2, s3, s4 = s1 / norm_s, s2 / norm_s, s3 / norm_s, s4 / norm_s

        # Compute the rate of change of quaternion from gyroscope
        gx, gy, gz = gyro
        q_dot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - self.beta * s1
        q_dot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - self.beta * s2
        q_dot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - self.beta * s3
        q_dot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - self.beta * s4

        # Integrate to yield new quaternion
        q1 += q_dot1 * self.sample_period
        q2 += q_dot2 * self.sample_period
        q3 += q_dot3 * self.sample_period
        q4 += q_dot4 * self.sample_period
        q_new = np.array([q1, q2, q3, q4])
        # Normalize quaternion
        self.q = q_new / np.linalg.norm(q_new)
        return self.q

    def get_euler(self):
        """
        Returns the current orientation as Euler angles (yaw, pitch, roll) in degrees.
        """
        q = self.q
        # Yaw (z-axis rotation)
        yaw = np.arctan2(2*(q[0]*q[1] + q[2]*q[3]),
                         1 - 2*(q[1]*q[1] + q[2]*q[2]))
        # Pitch (y-axis rotation)
        pitch = np.arcsin(2*(q[0]*q[2] - q[3]*q[1]))
        # Roll (x-axis rotation)
        roll = np.arctan2(2*(q[0]*q[3] + q[1]*q[2]),
                          1 - 2*(q[2]*q[2] + q[3]*q[3]))
        return np.degrees(yaw), np.degrees(pitch), np.degrees(roll)
    
    def get_rotation_matrix(self):
        """
        Returns the 3x3 rotation matrix corresponding to the current quaternion.
        """
        q = self.q
        # Compute the rotation matrix elements
        r11 = 1 - 2*(q[2]**2 + q[3]**2)
        r12 = 2*(q[1]*q[2] - q[0]*q[3])
        r13 = 2*(q[1]*q[3] + q[0]*q[2])
        r21 = 2*(q[1]*q[2] + q[0]*q[3])
        r22 = 1 - 2*(q[1]**2 + q[3]**2)
        r23 = 2*(q[2]*q[3] - q[0]*q[1])
        r31 = 2*(q[1]*q[3] - q[0]*q[2])
        r32 = 2*(q[2]*q[3] + q[0]*q[1])
        r33 = 1 - 2*(q[1]**2 + q[2]**2)
        return np.array([[r11, r12, r13],
                         [r21, r22, r23],
                         [r31, r32, r33]])

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    data = pd.read_csv('Trial1_X_extracted.csv')
    data.head()

    times = data['Timestamp'].to_numpy()
    print(times)
    N = len(times)
    gyro_data = data[['Gyro_X', 'Gyro_Y', 'Gyro_Z']].to_numpy()
    accel_data = data[['Accel_X', 'Accel_Y', 'Accel_Z']].to_numpy()
    mag_data = data[['Mag_X', 'Mag_Y', 'Mag_Z']].to_numpy()

    quaternions = np.zeros((N, 4))
    euler_angles = np.zeros((N, 3))  # yaw, pitch, roll
    global_acc = np.zeros((N, 3))
    velocity = np.zeros((N, 3))
    position = np.zeros((N, 3))

    avg_dt = np.mean(times)
    madgwick = MadgwickFilter(sample_period=avg_dt, beta=0.1)

    # Arrays to store orientation (Euler angles) at each time step
    yaw_list = []
    pitch_list = []
    roll_list = []

    for i in range(N):
        # Update the sample period for current time step
        current_dt = times[i] if times[i] > 0 else avg_dt
        madgwick.sample_period = current_dt

        # Update the filter with current sensor data
        q = madgwick.update(gyro=gyro_data[i], accel=accel_data[i], mag=mag_data[i])
        quaternions[i] = q
        euler_angles[i] = madgwick.get_euler()
        
        # Get rotation matrix and rotate accelerometer vector to global frame
        R = madgwick.get_rotation_matrix()
        global_acc[i] = R @ accel_data[i]
        
        # Integrate to compute velocity and position (using Euler integration)
        if i > 0:
            dt = times[i]
            velocity[i] = velocity[i-1] + global_acc[i-1] * dt
            position[i] = position[i-1] + velocity[i-1] * dt + 0.5 * global_acc[i-1] * dt**2

    # --- Step 5: Compute Displacement ---
    overall_displacement = np.linalg.norm(position[-1] - position[0])
    cumulative_disp = np.zeros(N)
    for i in range(1, N):
        step_disp = np.linalg.norm(position[i] - position[i-1])
        cumulative_disp[i] = cumulative_disp[i-1] + step_disp
    
    # --- Step 6: Store Results in a DataFrame ---
    data['yaw_deg'] = euler_angles[:, 0]
    data['pitch_deg'] = euler_angles[:, 1]
    data['roll_deg'] = euler_angles[:, 2]

    data['vel_x'] = velocity[:, 0]
    data['vel_y'] = velocity[:, 1]
    data['vel_z'] = velocity[:, 2]

    data['pos_x'] = position[:, 0]
    data['pos_y'] = position[:, 1]
    data['pos_z'] = position[:, 2]

    data['cumulative_displacement'] = cumulative_disp

    print("Overall displacement (net):", data['cumulative_displacement'][-1])

    # Save to a new CSV if desired
    data.to_csv('Trial1_X_fusion.csv', index=False)
