from force_reader_threading import get_latest_angles, start_serial_thread, stop_serial_thread
from quadrant_detection import determine_quadrant
import time
import os
import shutil

start_serial_thread()

def store_data(file_path, name):
    directory_path = "bootcamp_data/" + name
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    shutil.move(file_path, os.path.join(directory_path, os.path.basename(file_path)))
    

def scan_angles():
<<<<<<< HEAD
    while True:
        n,s,e,w, = get_latest_angles()
        with open("output.txt", "w") as f:
            f.write()
        print(determine_quadrant(n,s,e,w))
        time.sleep(0.2)
=======
    with open("quadrant_log.txt", "a") as f:
        while True:
                        
            n, s, e, w = get_latest_angles()
            quadrant = determine_quadrant(n, s, e, w)
            print(quadrant)
            f.write(f"{time.time()},{quadrant}\n")  # save timestamp + flex sensor data
            f.flush()  # ensure data is written immediately
            time.sleep(0.2)
>>>>>>> f610de155418669eaea8481d8ae2082f7481f48f
        

if __name__ == "__main__":
    store_data("test2.txt", "joe")
    #scan_angles()
