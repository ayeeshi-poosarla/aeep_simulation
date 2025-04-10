import re

def parse(line):
    pattern_time = re.compile(r'(\d+\.\d+) s')
    pattern_accel = re.compile(r'Accel X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+) m/s\^2')
    pattern_gyro = re.compile(r'Gyro X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)radians/s')
    pattern_mag = re.compile(r'Mag X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)uT')

    match_time = pattern_time.search(line)
    if match_time:
        current_time = float(match_time.group(1))
    
    match_accel = pattern_accel.search(line)
    if match_accel:
        dt = current_time
        ax = float(match_accel.group(1))
        ay = float(match_accel.group(2))
        az = float(match_accel.group(3))

    match_gyro = pattern_gyro.search(line)
    if match_gyro:
        gx = float(match_gyro.group(1))
        gy = float(match_gyro.group(2))
        gz = float(match_gyro.group(3))
    
    match_mag = pattern_mag.search(line)
    if match_mag:
        mx = float(match_mag.group(1))
        my = float(match_mag.group(2))
        mz = float(match_mag.group(3))

    return dt, ax, ay, az, gx, gy, gz, mx, my, mz

# Example usage
# dof9_line = "0.069569 s Accel X: 0.14 Y: 0.73 Z: 0.26 m/s^2 Mag X: -5.70 Y: 7.20 Z: -8.00uT Gyro X: -0.00 Y: -0.01 Z: 0.01radians/s"
# parse(dof9_line)