import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import csv
import fixedendpointtest

def read_imu_data(csv_path):
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = float(row['Timestamp'])
            accel = np.array([float(row['Accel_X']), float(row['Accel_Y']), float(row['Accel_Z'])])
            gyro  = np.array([float(row['Gyro_X']),  float(row['Gyro_Y']),  float(row['Gyro_Z'])])
            mag   = np.array([float(row['Mag_X']),   float(row['Mag_Y']),   float(row['Mag_Z'])])
            yield ts, gyro, accel, mag
  # Example length of the rod
def static_orientation_test(tracker, data_path, expected_angle_deg, axis='z', tol_deg=5):
    """
    Tests whether the estimated orientation matches a known static angle.
    Parameters:
    - tracker: RodTracker instance
    - data_path: Path to the CSV data
    - expected_angle_deg: Expected rotation in degrees
    - axis: Rotation axis ('x', 'y', or 'z')
    - tol_deg: Acceptable tolerance in degrees
    """
    from scipy.spatial.transform import Rotation as R
    from collections import deque

    angle_errors = deque()

    for ts, gyro, accel, mag in read_imu_data(data_path):
        tip, quat, _ = tracker.update(gyro, accel, mag, ts)
        rot = R.from_quat([quat[1], quat[2], quat[3], quat[0]])  # x,y,z,w
        euler = rot.as_euler('xyz', degrees=True)

        measured_angle = {'x': euler[0], 'y': euler[1], 'z': euler[2]}[axis]
        angle_errors.append(measured_angle)

    avg_measured = np.mean(angle_errors)
    error = abs(avg_measured - expected_angle_deg)

    print(f"[Static Orientation Test @ {expected_angle_deg}° {axis}-axis]")
    print(f"→ Average Measured: {avg_measured:.2f}° | Error: {error:.2f}°")

    #assert error < tol_deg, f"Orientation error {error:.2f}° exceeds tolerance of {tol_deg}°."

    return avg_measured, error

def insertion_depth_test(tracker, data_path, true_depth_m, tol_mm=1.0):
    depths = []

    for ts, gyro, accel, mag in read_imu_data(data_path):
        _, _, depth = tracker.update(gyro, accel, mag, ts)
        depths.append(depth)

    avg_depth = np.mean(depths)
    error_mm = abs(avg_depth - true_depth_m) * 1000

    print(f"[Insertion Depth Test @ {true_depth_m:.3f} m]")
    print(f"→ Avg Measured Depth: {avg_depth:.3f} m | Error: {error_mm:.1f} mm")

    assert error_mm < tol_mm, f"Depth error {error_mm:.1f} mm exceeds tolerance of {tol_mm} mm."
    return avg_depth, error_mm

def rotation_circle_test(tracker, data_path, expected_radius_m, axis='z'):
    from collections import deque

    tips = deque()
    for ts, gyro, accel, mag in read_imu_data(data_path):
        tip, _, _ = tracker.update(gyro, accel, mag, ts)
        tips.append(tip)

    tips = np.array(tips)
    plane = {'x': [1, 2], 'y': [0, 2], 'z': [0, 1]}[axis]
    traj = tips[:, plane]
    center = np.mean(traj, axis=0)
    distances = np.linalg.norm(traj - center, axis=1)
    mean_r = np.mean(distances)
    rms_error = np.sqrt(np.mean((distances - expected_radius_m)**2))

    print(f"[Rotation Sweep Test]")
    print(f"→ Mean Radius: {mean_r:.3f} m | RMS Radial Error: {rms_error:.3f} m")

    plt.figure()
    plt.title("XY Tip Path (Circle Test)")
    plt.plot(traj[:,0], traj[:,1], label='Estimated Path')
    plt.gca().set_aspect('equal')
    plt.legend()
    plt.grid(True)
    plt.show()

    return mean_r, rms_error

tracker = fixedendpointtest.RodTracker(L=0.13)
static_orientation_test(tracker, "testing/data/4_27_25/20fromNorth.csv", expected_angle_deg=0, axis='z')
static_orientation_test(tracker, "testing/data/4_24_25/20_degree.csv", expected_angle_deg=20, axis='z')
static_orientation_test(tracker, "testing/data/4_24_25/40_degree.csv", expected_angle_deg=40, axis='z')
static_orientation_test(tracker, "testing/data/4_24_25/60_degree.csv", expected_angle_deg=60, axis='z')
static_orientation_test(tracker, "testing/data/4_24_25/90_degree.csv", expected_angle_deg=90, axis='z')
#insertion_depth_test(tracker, "tests/insert_5cm.csv", true_depth_m=0.05)
#rotation_circle_test(tracker, "tests/rotate_circle_25cm.csv", expected_radius_m=0.25