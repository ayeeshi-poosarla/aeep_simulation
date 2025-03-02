import re
import numpy as np

data_file = "minimap/accelgyro.txt"
with open(data_file, "r") as file:
    lines = file.readlines()

accelerations = []
for line in lines:
    match_ax = re.search(r"Ax=([-\d.]+)", line)
    match_ay = re.search(r"Ay=([-\d.]+)", line)
    match_az = re.search(r"Az=([-\d.]+)", line)
    
    if match_ax and match_ay and match_az:
        ax = float(match_ax.group(1))
        ay = float(match_ay.group(1))
        az = float(match_az.group(1))

    accelerations.append([ax, ay, az])

for vector in accelerations:
    print(vector)
