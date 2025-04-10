import re
import pandas as pd

# Replace with your input file path
file_path = 'Trial 2 Y_Direction_ReDo.txt'

# Lists to store extracted data
time_stamps, accel_x, accel_y, accel_z = [], [], [], []
gyro_x, gyro_y, gyro_z = [], [], []
mag_x, mag_y, mag_z = [], [], []

# Regex patterns
pattern_time = re.compile(r'(\d+\.\d+) s')
pattern_accel = re.compile(r'Accel X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+) m/s\^2')
pattern_gyro = re.compile(r'Gyro X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)radians/s')
pattern_mag = re.compile(r'Mag X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)uT')

with open(file_path, 'r') as file:
    for line in file:
        # Extract timestamps
        match_time = pattern_time.search(line)
        if match_time:
            current_time = float(match_time.group(1))
        
        # Extract acceleration
        match_accel = pattern_accel.search(line)
        if match_accel:
            time_stamps.append(current_time)
            accel_x.append(float(match_accel.group(1)))
            accel_y.append(float(match_accel.group(2)))
            accel_z.append(float(match_accel.group(3)))

        # Extract gyroscope
        match_gyro = pattern_gyro.search(line)
        if match_gyro:
            gyro_x.append(float(match_gyro.group(1)))
            gyro_y.append(float(match_gyro.group(2)))
            gyro_z.append(float(match_gyro.group(3)))
        
        # Extract magnetometer
        match_mag = pattern_mag.search(line)
        if match_mag:
            mag_x.append(float(match_mag.group(1)))
            mag_y.append(float(match_mag.group(2)))
            mag_z.append(float(match_mag.group(3)))

# Ensure all lists are of the same length
max_length = max(len(time_stamps), len(accel_x), len(accel_y), len(accel_z),
                 len(gyro_x), len(gyro_y), len(gyro_z),
                 len(mag_x), len(mag_y), len(mag_z))
time_stamps = time_stamps[:max_length]
accel_x = accel_x[:max_length]
accel_y = accel_y[:max_length]
accel_z = accel_z[:max_length]
gyro_x = gyro_x[:max_length]
gyro_y = gyro_y[:max_length]
gyro_z = gyro_z[:max_length]
mag_x = mag_x[:max_length]
mag_y = mag_y[:max_length]
mag_z = mag_z[:max_length]

# Create DataFrame
data = pd.DataFrame({
    'Timestamp': time_stamps,
    'Accel_X': accel_x,
    'Accel_Y': accel_y,
    'Accel_Z': accel_z,
    'Gyro_X': gyro_x,
    'Gyro_Y': gyro_y,
    'Gyro_Z': gyro_z,
    'Mag_X': mag_x,
    'Mag_Y': mag_y,
    'Mag_Z': mag_z
})

# Save to CSV
data.to_csv('Trial2_Y_extracted.csv', index=False)

print(data.head())