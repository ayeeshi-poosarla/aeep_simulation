import serial
import numpy as np
import time
from ahrs.filters import Madgwick

def quat_to_rot_matrix(q):
    """
    Convert a quaternion (w, x, y, z) into a 3x3 rotation matrix.
    """
    w, x, y, z = q
    R = np.array([
        [1 - 2*(y**2 + z**2), 2*(x*y - z*w),     2*(x*z + y*w)],
        [2*(x*y + z*w),       1 - 2*(x**2 + z**2), 2*(y*z - x*w)],
        [2*(x*z - y*w),       2*(y*z + x*w),     1 - 2*(x**2 + y**2)]
    ])
    return R

# --- Setup serial communication ---
# Change the port and baud rate to match your IMU configuration.
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# --- Initialize the Madgwick filter ---
madgwick = Madgwick()  # Default parameters; adjust beta if needed

# --- Initialize state variables ---
q = np.array([1.0, 0.0, 0.0, 0.0])  # initial quaternion (w, x, y, z)
velocity = np.zeros(3)              # initial velocity (m/s)
position = np.zeros(3)              # initial position (m)
prev_time = time.time()

print("Starting real-time position tracking. Press Ctrl+C to stop.")
try:
    while True:
        # Read a line of data from the IMU. Expected format:
        # "ax,ay,az,gx,gy,gz,mx,my,mz"
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue
        try:
            # Convert the comma-separated string into a list of floats.
            data = [float(x) for x in line.split(',')]
            if len(data) != 9:
                continue  # skip lines with missing data
            # Extract sensor measurements:
            ax, ay, az = data[0:3]          # acceleration (m/s^2)
            gx, gy, gz = data[3:6]          # gyroscope (rad/s)
            mx, my, mz = data[6:9]          # magnetometer (uT)
        except ValueError:
            continue  # skip any malformed data
        
        # Compute time step
        current_time = time.time()
        dt = current_time - prev_time
        prev_time = current_time
        
        # Create numpy arrays for the sensor data
        acc = np.array([ax, ay, az])
        gyro = np.array([gx, gy, gz])  # already in rad/s
        mag = np.array([mx, my, mz])
        
        # --- Sensor Fusion: update orientation estimate ---
        q = madgwick.updateIMU(q, gyr=gyro, acc=acc, dt=dt)
        
        # --- Transform acceleration to world frame ---
        R = quat_to_rot_matrix(q)
        acc_world = R.dot(acc)
        
        # Remove the gravity component (assuming gravity ~9.81 m/s^2 along the world Z axis)
        acc_linear = acc_world - np.array([0, 0, 9.81])
        
        # --- Numerical Integration to Estimate Velocity and Position ---
        velocity += acc_linear * dt  # simple Euler integration for velocity
        position += velocity * dt      # and then for position
        
        # Display the current estimated position
        print("Position (m):", position)
        
except KeyboardInterrupt:
    print("Stopping tracking.")
finally:
    ser.close()
