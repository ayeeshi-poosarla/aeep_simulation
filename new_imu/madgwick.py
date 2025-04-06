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


# =============================================================================
# Example usage: Data fusion and storing results in a DataFrame
# =============================================================================
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # Suppose you have arrays of sensor data recorded from your 9-DOF IMU.
    # Here we simulate some dummy data for demonstration.
    # (In practice, replace these with your actual data arrays.)
    n_samples = 200
    sample_period = 1 / 256  # for example, 256 Hz sample rate
    times = np.linspace(0, (n_samples - 1) * sample_period, n_samples)
    
    # Simulated sensor readings:
    # For a static tool (no rotation), gyroscope outputs zeros.
    gyro_data = np.zeros((n_samples, 3))
    # Accelerometer: assume the sensor is stationary with gravity acting along Z.
    # (If your sensor outputs m/s^2, gravity ≈ 9.81 m/s^2; here we use a unit vector.)
    accel_data = np.tile(np.array([0.0, 0.0, 1.0]), (n_samples, 1))
    # Magnetometer: assume a constant Earth magnetic field vector in sensor frame.
    mag_data = np.tile(np.array([0.5, 0.0, 0.0]), (n_samples, 1))

    # Initialize the filter
    madgwick = MadgwickFilter(sample_period=sample_period, beta=0.1)

    # Arrays to store orientation (Euler angles) at each time step
    yaw_list = []
    pitch_list = []
    roll_list = []

    # Process each sensor sample
    for i in range(n_samples):
        q = madgwick.update(gyro=gyro_data[i],
                            accel=accel_data[i],
                            mag=mag_data[i])
        yaw, pitch, roll = madgwick.get_euler()
        yaw_list.append(yaw)
        pitch_list.append(pitch)
        roll_list.append(roll)

    # Build a DataFrame with the results
    df_results = pd.DataFrame({
        'Time (s)': times,
        'Yaw (deg)': yaw_list,
        'Pitch (deg)': pitch_list,
        'Roll (deg)': roll_list
    })

    # Display the first few rows
    print(df_results.head())

    # Optionally, save or further process the DataFrame.
    # For example, you might write it to a CSV file:
    # df_results.to_csv("orientation_results.csv", index=False)
