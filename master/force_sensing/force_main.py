from force_reader_threading import get_latest_angles, start_serial_thread, stop_serial_thread
from quadrant_detection import determine_quadrant
import keyboard

start_serial_thread()

def scan_angles():
    while True:
        n,s,e,w, = get_latest_angles()
        print(determine_quadrant(n,s,e,w))
        
        if keyboard.is_pressed("esc"):
            stop_serial_thread
            break

if __name__ == "__main":
    scan_angles()