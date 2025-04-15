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
        # For brevity, the combined gradient terms are approximated as:
        s1 = -_2q3 * f1 + _2q2 * f2
        s2 = _2q4 * f1 + _2q1 * f2 - 4.0 * q2 * f3
        s3 = -_2q1 * f1 + _2q4 * f2 - 4.0 * q3 * f3
        s4 = _2q2 * f1 + _2q3 * f2
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
    
    def compute_position(self, data):
        """
        Processes a sequence of IMU sensor data to compute the IMU's position over time.
        
        The input `data` should be an array-like object of shape (N, 10), where each row is:
            [dt, ax, ay, az, gx, gy, gz, mx, my, mz]
        with:
            dt   : Sample period (in seconds) for the current measurement.
            ax, ay, az : Accelerometer readings.
            gx, gy, gz : Gyroscope readings (in rad/s).
            mx, my, mz : Magnetometer readings.
        
        The function updates the Madgwick filter to compute orientation, rotates the accelerometer
        measurements into the global frame, and then integrates to compute velocity and position.
        
        Returns:
        --------
        position : ndarray
            An array of shape (N, 3) containing the [x, y, z] positions computed at each time step.
        """
        data = np.array(data)
        N = data.shape[0]
        
        # Allocate arrays to store results
        quaternions = np.zeros((N, 4))
        euler_angles = np.zeros((N, 3))  # yaw, pitch, roll
        global_acc = np.zeros((N, 3))
        velocity = np.zeros((N, 3))
        position = np.zeros((N, 3))
        
        # Loop over each sensor measurement
        for i in range(N):
            # Extract sensor measurements from the current row
            dt = data[i, 0]
            accel = data[i, 1:4]    # ax, ay, az
            gyro  = data[i, 4:7]    # gx, gy, gz
            mag   = data[i, 7:10]   # mx, my, mz
            
            # Update the sample period for the filter at this time step
            self.sample_period = dt
            
            # Update the filter with the current sensor data
            q = self.update(gyro=gyro, accel=accel, mag=mag)
            quaternions[i] = q
            euler_angles[i] = self.get_euler()
            
            # Compute rotation matrix from the current orientation
            R = self.get_rotation_matrix()
            # Rotate the accelerometer reading into the global frame
            global_acc[i] = R @ accel
            
            # Integrate the global acceleration to compute velocity and position
            if i > 0:
                velocity[i] = velocity[i-1] + global_acc[i] * dt
                position[i] = position[i-1] + velocity[i-1] * dt + 0.5 * global_acc[i] * (dt ** 2)
        
        return position

def calibrate_magnetometer(mag_data):
    """
    Calibrates raw magnetometer data using hard and soft iron correction.
    
    Parameters:
    -----------
    mag_data : ndarray
        Raw magnetometer measurements of shape (N, 3).
        
    Returns:
    --------
    calibrated_mag_data : ndarray
        The calibrated magnetometer data.
    """
    calibrated_mag_data = np.zeros_like(mag_data)
    # Hard iron bias
    B = np.array([109.06238802, 37.90448955, 125.2127988])
    # Inverse of soft iron matrix
    A_inv = np.array([[2.58891148, 0.03830976, -0.05865281],
                      [0.03830976, 2.79695092, 0.03519644],
                      [-0.05865281, 0.03519644, 2.72060039]])
    
    for i in range(mag_data.shape[0]):
        # Subtract hard iron bias
        mag_data[i] = mag_data[i] - B
        # Apply soft iron transformation
        calibrated_mag_data[i] = np.dot(mag_data[i], A_inv)
    return calibrated_mag_data


# Example usage:
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # For demonstration, assume we load sensor data from a CSV file.
    # The CSV should have columns: dt, ax, ay, az, gx, gy, gz, mx, my, mz
    # Here, we simulate loading such a CSV file.
    df = pd.read_csv('testing/new_imu/Trial1_Y_extracted.csv')
    
    # For this example, we select a subset of the data starting at a given index.
    mask = df['Mag_X'] < -1500
    start_index = df[mask].index[0]
    data_df = df.loc[start_index:]
    
    # Convert the relevant columns into a NumPy array in the correct order.
    # Here we assume that "Timestamp" holds dt values (sample periods),
    # and the rest of the columns correspond to ax, ay, az, gx, gy, gz, mx, my, mz.
    sensor_data = data_df[['Timestamp', 'Accel_X', 'Accel_Y', 'Accel_Z',
                             'Gyro_X', 'Gyro_Y', 'Gyro_Z',
                             'Mag_X', 'Mag_Y', 'Mag_Z']].to_numpy()
    
    # Optionally, calibrate the magnetometer data
    mag_data = sensor_data[:, 7:10]
    sensor_data[:, 7:10] = calibrate_magnetometer(mag_data)
    
    # Create an instance of MadgwickFilter; initial sample period is set from the first row.
    initial_dt = sensor_data[0, 0]
    madgwick = MadgwickFilter(sample_period=initial_dt, beta=0.1)
    
    # Compute the position of the IMU for the entire data sequence
    position = madgwick.compute_position(sensor_data)
    print(position)
    
    overall_displacement = np.linalg.norm(position[-1] - position[0])
    print("Overall displacement (net):", overall_displacement)
    
    # Optionally, save the computed positions to CSV.
    pos_df = pd.DataFrame(position, columns=['pos_x', 'pos_y', 'pos_z'])
    pos_df.to_csv('Trial1_Y_fusion_positions.csv', index=False)
    
    # Plot the position trajectory if desired.
    plt.figure()
    plt.plot(position[:, 0], position[:, 1], label='Trajectory (x-y)')
    plt.xlabel('Position X')
    plt.ylabel('Position Y')
    plt.title('IMU Trajectory')
    plt.legend()
    plt.show()
