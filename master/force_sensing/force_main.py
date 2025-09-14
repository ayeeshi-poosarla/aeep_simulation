from force_reader_threading import get_latest_angles, start_serial_thread, stop_serial_thread
from quadrant_detection import determine_quadrant
import time

start_serial_thread()

def scan_angles():
    while True:
        n,s,e,w, = get_latest_angles()
        print(determine_quadrant(n,s,e,w))
        time.sleep(0.2)
        

if __name__ == "__main__":
    scan_angles()