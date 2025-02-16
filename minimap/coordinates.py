import re
import numpy as np

def compute_positions_from_file(filename, dt=0.01):
    """Reads acceleration data from file, integrates it to estimate position."""
    accel_x, accel_y, accel_z = [], [], []
    pattern = re.compile(r"Ax=(-?\d+\.\d+).+?Ay=(-?\d+\.\d+).+?Az=(-?\d+\.\d+)")

    # Read and extract acceleration data
    with open(filename, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                ax, ay, az = map(float, match.groups())
                accel_x.append(ax)
                accel_y.append(ay)
                accel_z.append(az)

    # Integrate acceleration to estimate velocity and position
    n = len(accel_x)
    velocity_x, velocity_y, velocity_z = np.zeros(n), np.zeros(n), np.zeros(n)
    position_x, position_y, position_z = np.zeros(n), np.zeros(n), np.zeros(n)

    for i in range(1, n):
        velocity_x[i] = velocity_x[i-1] + accel_x[i] * dt
        velocity_y[i] = velocity_y[i-1] + accel_y[i] * dt
        velocity_z[i] = velocity_z[i-1] + accel_z[i] * dt

        position_x[i] = position_x[i-1] + velocity_x[i] * dt
        position_y[i] = position_y[i-1] + velocity_y[i] * dt
        position_z[i] = position_z[i-1] + velocity_z[i] * dt

    return position_x, position_y, position_z

# Call the function
filename = "accelgyro.txt"
positions_x, positions_y, positions_z = compute_positions_from_file(filename)

print("Estimated Positions (X, Y, Z):")
print("X:", positions_x)
print("Y:", positions_y)
print("Z:", positions_z)
