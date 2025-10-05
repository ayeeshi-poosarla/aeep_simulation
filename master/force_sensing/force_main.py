from force_reader_threading import get_latest_angles, start_serial_thread
from quadrant_detection import determine_quadrant
from conductive_reader_threading import *
import time
import os
import shutil
import csv

start_serial_thread()

def store_data(file_path, name):
    directory_path = "bootcamp_data/" + name
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    shutil.move(file_path, os.path.join(directory_path, os.path.basename(file_path)))
    

def scan_angles():
    new_file_1 = not os.path.exists("quadrant_log.csv")
    new_file_2 = not os.path.exists("force_log.csv")

    with open("quadrant_log.csv", "a", newline='') as f1, open("force_log.csv", "a", newline='') as f2:
        quadrant_writer = csv.writer(f1)
        force_writer = csv.writer(f2)

        if new_file_1:
            quadrant_writer.writerow(["timestamp", "quadrant"])
        if new_file_2:
            force_writer.writerow(["timestamp", "N", "S", "E", "W"])

        while True:
            n, s, e, w = get_latest_angles()
            latest_sheet = get_latest_sheet()
            quadrant = determine_quadrant(n, s, e, w)
            timestamp = time.time()

            print(quadrant)
            quadrant_writer.writerow([timestamp, quadrant])
            force_writer.writerow([timestamp, *latest_sheet])
            f1.flush()
            f2.flush()

            time.sleep(0.2)
        

if __name__ == "__main__":
    store_data("test2.txt", "joe")
    #scan_angles()
