import re
import numpy as np

pattern = r"Acceleration\s+X:\s*([-\d.]+)\s*,\s*Y:\s*([-\d.]+)\s*,\s*Z:\s*([-\d.]+)"

# Lists to store time values and acceleration vectors.
times = []
accelerations = []

with open("data/imu_data.txt", "r") as file:
    lines = file.readlines()

i = 0
while i < len(lines):
    # Get the time stamp (first non-empty line in the block)
    line = lines[i].strip()
    if not line:
        i += 1
        continue

    try:
        t = float(line)
        times.append(t)
    except ValueError:
        i += 1
        continue

    # Skip the next non-empty line (rotation data)
    i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Now, skip the rotation data line
    if i < len(lines):
        i += 1  # skip rotation data line

    # Skip any empty lines before the acceleration data line
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Next non-empty line should be the acceleration data line.
    if i < len(lines):
        acc_line = lines[i].strip()
        match = re.search(pattern, acc_line)
        if match:
            ax = float(match.group(1))
            ay = float(match.group(2))
            az = float(match.group(3))
            accelerations.append([ax, ay, az])
        else:
            print("Regex did not match acceleration line:", acc_line)
    
    i += 1

# Display the stored arrays.
print("Time values:", times)
print("Acceleration vectors:", accelerations)

initial_time = times[0] 
initial_acceleration = accelerations[0]

initial_velocity = [accelerations[0][0] * initial_time, accelerations[0][1] * initial_time, 
    accelerations[0][2] * initial_time]

initial_position = [0.5 * accelerations[0][0] * (initial_time**2), 
    0.5 * accelerations[0][1] * (initial_time**2), 0.5 * accelerations[0][0] * (initial_time**2)]

for i in range(1, len(times)):
    time = times[i]
    acceleration = accelerations[i]

    velocity = [initial_velocity[0] + (acceleration[0] * time), 
        initial_velocity[1] + (acceleration[1] * time), initial_velocity[2] + (acceleration[2] * time)]

    position = [initial_position[0] + (initial_velocity[0] * time) + (0.5 * acceleration[0] * (time ** 2)),
        initial_position[1] + (initial_velocity[1] * time) + (0.5 * acceleration[1] * (time ** 2)), 
        initial_position[2] + (initial_velocity[2] * time) + (0.5 * acceleration[2] * (time ** 2))]
    
    print(position)
    initial_velocity = velocity
    initial_position = position
    initial_time = times[i]