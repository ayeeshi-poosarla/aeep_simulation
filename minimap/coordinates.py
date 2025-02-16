import re
import numpy as np

def extract_sensor_data(filename):
    """Extracts acceleration (Ax, Ay, Az) from sensor file."""
    accel_x, accel_y, accel_z = [], [], []
    pattern = re.compile(r"Ax=(-?\d+\.\d+).+?Ay=(-?\d+\.\d+).+?Az=(-?\d+\.\d+)")

    with open(filename, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                ax, ay, az = map(float, match.groups())
                accel_x.append(ax)
                accel_y.append(ay)
                accel_z.append(az)

    return accel_x, accel_y, accel_z

def integrate_acceleration(accel_x, accel_y, accel_z, dt=0.01):
    """Integrates acceleration to estimate velocity and position."""
    n = len(accel_x)
    velocity_x, velocity_y, velocity_z = np.zeros(n), np.zeros(n), np.zeros(n)
    position_x, position_y, position_z = np.zeros(n), np.zeros(n), np.zeros(n)

    for i in range(1, n):
        # Velocity = Previous velocity + (acceleration * time step)
        velocity_x[i] = velocity_x[i-1] + accel_x[i] * dt
        velocity_y[i] = velocity_y[i-1] + accel_y[i] * dt
        velocity_z[i] = velocity_z[i-1] + accel_z[i] * dt

        # Position = Previous position + (velocity * time step)
        position_x[i] = position_x[i-1] + velocity_x[i] * dt
        position_y[i] = position_y[i-1] + velocity_y[i] * dt
        position_z[i] = position_z[i-1] + velocity_z[i] * dt

    return position_x, position_y, position_z

# Read acceleration from file
filename = "accelgyro.txt"
accel_x, accel_y, accel_z = extract_sensor_data(filename)

# Integrate acceleration to get position
positions_x, positions_y, positions_z = integrate_acceleration(accel_x, accel_y, accel_z)

print("Estimated Positions (X, Y, Z):")
print("X:", positions_x)
print("Y:", positions_y)
print("Z:", positions_z)
