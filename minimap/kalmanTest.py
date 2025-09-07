import numpy as np
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter

# --------------------------------------------
# Step 1: Load IMU Data from CSV
# --------------------------------------------
def read_imu_csv(filename):
    data = np.genfromtxt(filename, delimiter=",", skip_header=1)
    timestamps = data[:, 0]
    accel_data = data[:, 1:4] / 100.0  # Convert cm/s^2 to m/s^2
    gyro_data = data[:, 4:7]
    return timestamps, accel_data, gyro_data

# --------------------------------------------
# Step 2: Fix Timestamps
# --------------------------------------------
def fix_timestamps(timestamps):
    if np.max(timestamps) > 1e3:
        timestamps = timestamps / 1000.0  # Assume input is in milliseconds
    for i in range(1, len(timestamps)):
        if timestamps[i] <= timestamps[i-1]:
            timestamps[i] = timestamps[i-1] + 0.001
    return timestamps

# --------------------------------------------
# Step 3: Calibration (initial samples)
# --------------------------------------------
def calibrate_sensors(accel_data, gyro_data, stationary_samples=10):
    accel_bias = np.mean(accel_data[:stationary_samples], axis=0)
    gyro_bias = np.mean(gyro_data[:stationary_samples], axis=0)
    calibrated_accel = accel_data - accel_bias
    calibrated_gyro = gyro_data - gyro_bias
    return calibrated_accel, calibrated_gyro

# --------------------------------------------
# Step 4: Stationary Detection (ZUPT)
# --------------------------------------------
def detect_stationary_periods(accel_data, window_size=5, threshold=0.01):
    accel_mag = np.linalg.norm(accel_data, axis=1)
    stationary = np.zeros(len(accel_mag), dtype=bool)
    for i in range(window_size, len(accel_mag)):
        if np.var(accel_mag[i - window_size:i]) < threshold:
            stationary[i] = True
    return stationary

# --------------------------------------------
# Step 5: Velocity and Position Integration
# --------------------------------------------
def compute_velocity_and_position(timestamps, accel_data):
    velocity = np.zeros_like(accel_data)
    position = np.zeros_like(accel_data)
    for i in range(1, len(timestamps)):
        dt = timestamps[i] - timestamps[i-1]
        velocity[i] = velocity[i-1] + 0.5 * (accel_data[i] + accel_data[i-1]) * dt
        position[i] = position[i-1] + 0.5 * (velocity[i] + velocity[i-1]) * dt
    return velocity, position

def apply_zupt_and_reintegrate(timestamps, accel_data, stationary):
    velocity = np.zeros_like(accel_data)
    position = np.zeros_like(accel_data)

    for i in range(1, len(timestamps)):
        dt = timestamps[i] - timestamps[i - 1]

        # Integrate acceleration to velocity
        velocity[i] = velocity[i - 1] + 0.5 * (accel_data[i] + accel_data[i - 1]) * dt

        # Apply ZUPT: if stationary, reset velocity
        if stationary[i]:
            velocity[i] = np.zeros(3)

        # Integrate velocity to position
        position[i] = position[i - 1] + 0.5 * (velocity[i] + velocity[i - 1]) * dt

    return velocity, position


# --------------------------------------------
# Step 8: Plotting
# --------------------------------------------
def plot_results(timestamps, raw_pos, zupt_pos, filtered_pos):
    plt.figure(figsize=(10, 6))
    plt.plot(raw_pos[:, 0], label='Raw X')
    plt.plot(zupt_pos[:, 0], label='ZUPT X')
    plt.plot(filtered_pos[:, 0], label='Filtered X')
    plt.title("X-axis Displacement Comparison")
    plt.xlabel("Sample")
    plt.ylabel("Position (m)")
    plt.legend()
    plt.grid()
    plt.show()

# --------------------------------------------
# Main
# --------------------------------------------
def main():
    filename = "accelgyro.txt"

    timestamps, accel_data, gyro_data = read_imu_csv(filename)
    timestamps = fix_timestamps(timestamps)

    # Calibration
    calibrated_accel, calibrated_gyro = calibrate_sensors(accel_data, gyro_data)

    # Integration
    raw_velocity, raw_position = compute_velocity_and_position(timestamps, calibrated_accel)

    # ZUPT
    # Detect stationary
    stationary = detect_stationary_periods(calibrated_accel)

    # Apply ZUPT and reintegrate
    corrected_velocity, zupt_position = apply_zupt_and_reintegrate(timestamps, calibrated_accel, stationary)

    # zupt_position = recompute_position(timestamps, corrected_velocity)

    # Kalman Filter
    filtered_states = apply_kalman_filter(timestamps, zupt_position, corrected_velocity)
    filtered_position = filtered_states[:, :3]

    # Plot
    plot_results(timestamps, raw_position, zupt_position, filtered_position)

    # Print Final Displacement
    displacement = np.linalg.norm(filtered_position[-1] - filtered_position[0])
    print(f"Final displacement: {displacement:.4f} meters")
    print(f"Stationary count: {np.sum(stationary)} out of {len(stationary)}")
    displacement = np.linalg.norm(zupt_position[-1] - zupt_position[0])
    print(f"Final estimated displacement: {displacement:.4f} meters")
    return raw_position, zupt_position, filtered_position

# --------------------------------------------
# Optional: Kalman Filter
# --------------------------------------------
def apply_kalman_filter(timestamps, position_data, velocity_data):
    kf = KalmanFilter(dim_x=6, dim_z=6)
    kf.x = np.zeros(6)
    kf.x[:3] = position_data[0]
    kf.x[3:] = velocity_data[0]

    kf.F = np.eye(6)
    kf.H = np.eye(6)
    kf.P *= 100
    kf.R = np.eye(6)
    kf.R[:3, :3] *= 5
    kf.R[3:, 3:] *= 0.5

    filtered = []
    for i in range(1, len(timestamps)):
        dt = timestamps[i] - timestamps[i-1]
        kf.F[:3, 3:] = np.eye(3) * dt

        q = np.eye(6)
        q[:3, :3] *= (dt ** 4) / 4
        q[:3, 3:] *= (dt ** 3) / 2
        q[3:, :3] *= (dt ** 3) / 2
        q[3:, 3:] *= (dt ** 2)
        kf.Q = q * 0.01

        kf.predict()
        z = np.concatenate([position_data[i], velocity_data[i]])
        kf.update(z)
        filtered.append(kf.x.copy())
    return np.array(filtered)

# Run
if __name__ == "__main__":
    main()
    
