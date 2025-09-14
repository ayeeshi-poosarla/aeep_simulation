import serial
import time
import re
from quadrant_detection import determine_quadrant
from threading import Thread

latest_angles = (0.0, 0.0, 0.0, 0.0)

def parse(data: str):
    """
    Parses the input string from the Arduino to extract directional angle values.

    The expected format in the string is something like:
    "Sensor 1 ( North ) | Angle: 12.34°"
    
    Parameters:
        data (str): A line of data received from the Arduino containing sensor directions and angles.

    Returns:
        dict: A dictionary mapping directions (e.g., "North", "South") to their corresponding float angle values.
    """
    # Regular expression to capture direction and angle
    pattern = r"Sensor \d+ \(\s*(\w+)\s*\)\s*\|\s*Angle:\s*([\d.]+)°"
    
    # Find all matches of the pattern
    matches = re.findall(pattern, data)
    
    # Convert matches to dictionary with direction as key and angle as float
    return {direction: float(angle) for direction, angle in matches}

def serial_loop(port='/dev/tty.usbmodem21101', baud_rate=115200):
    """ Continuously read serial and update latest_angles """
    global latest_angles
    try:
        with serial.Serial(port, baud_rate, timeout=1) as arduino:
            time.sleep(2) 
            while True:
                inline = arduino.readline().decode('utf-8', errors="ignore").strip()
                if not inline:
                    continue
                dire = parse(inline)
                if dire:
                    north = dire.get("North", 0.0)
                    south = dire.get("South", 0.0)
                    east = dire.get("East", 0.0)
                    west = dire.get("West", 0.0)
                    latest_angles = (north, south, east, west)
    except Exception as e:
        print(f"[Serial error] {e}")

def start_serial_thread(port='/dev/tty.usbmodem21101', baud_rate=115200):
    thread = Thread(target=serial_loop, args=(port, baud_rate), daemon=True)
    thread.start()
    return thread

def get_latest_angles():
    return latest_angles

def stop_serial_thread():
    """ Signal the serial loop to stop """
    global stop_flag
    stop_flag = True