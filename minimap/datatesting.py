import re
import numpy
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

def positional():
    coordinates_file = "minimap/coordinates.txt"
    f = open(coordinates_file, "w")
    initial_time = times[0] 

    initial_velocity = [accelerations[0][0] * initial_time, accelerations[0][1] * initial_time, 
        accelerations[0][2] * initial_time]

    initial_position = [0.5 * accelerations[0][0] * (initial_time**2), 
        0.5 * accelerations[0][1] * (initial_time**2), 0.5 * accelerations[0][2] * (initial_time**2)]
    f.write(' '.join(map(str, initial_position)))
    f.write("\n")

    for i in range(1, len(times)):
        time = times[i]
        acceleration = accelerations[i]

        velocity = [initial_velocity[0] + (acceleration[0] * time), 
            initial_velocity[1] + (acceleration[1] * time), initial_velocity[2] + (acceleration[2] * time)]

        position = [initial_position[0] + (initial_velocity[0] * time) + (0.5 * acceleration[0] * (time ** 2)),
            initial_position[1] + (initial_velocity[1] * time) + (0.5 * acceleration[1] * (time ** 2)), 
            initial_position[2] + (initial_velocity[2] * time) + (0.5 * acceleration[2] * (time ** 2))]
        f.write(' '.join(map(str, position)))
        f.write("\n")
        
        initial_velocity = velocity
        initial_position = position
        initial_time = times[i]

pattern = r"Rotation\s+X:\s*([-\d.]+)\s*,\s*Y:\s*([-\d.]+)\s*,\s*Z:\s*([-\d.]+)"

    # Lists to store time values and rotation vectors.
times = []
rotations = []

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

        # Skip any empty lines until the next non-empty line (which should be the rotation data)
        i += 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1

        # Next non-empty line should be the rotation data line.
        if i < len(lines):
            rot_line = lines[i].strip()
            match = re.search(pattern, rot_line)
            if match:
                rx = float(match.group(1))
                ry = float(match.group(2))
                rz = float(match.group(3))
                rotations.append([rx, ry, rz])
            else:
                print("Regex did not match rotation line:", rot_line)
        
        # Skip the next non-empty line (which is now the acceleration data) to move to the next block.
        i += 1

def angular(i,time):
    d0 = [0,0,1] #initial unit direction vector
    angle_x = rotations[i][0] * time
    angle_y = rotations[i][1] * time
    angle_z = rotations[i][2] * time
    print(angle_x, angle_y, angle_z) #angle in radians

def run():
    positional()
    position_vectors = []

    with open("minimap/coordinates.txt", "r") as file:
        for line in file:
            # Skip empty lines
            if line.strip():
                vector = list(map(float, line.strip().split()))
                position_vectors.append(vector)

    # Optional: print all the vectors
    length = 0.25
    for i in range(len(times)):
        print(position_vectors[i])
        angular(i,times[i])
run()