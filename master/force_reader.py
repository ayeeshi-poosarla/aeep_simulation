import serial
import time
import re

def parse(data: str):
    pattern = r"Sensor \d+ \(\s*(\w+)\s*\)\s*\|\s*Angle:\s*([\d.]+)°"
    matches = re.findall(pattern, data)
    return {direction: float(angle) for direction, angle in matches}

def read_flex_data(port='/dev/ttyACM0', baud_rate=9600):
    with serial.Serial(port, baud_rate) as arduino:
        time.sleep(2)
        inline = arduino.readline().decode('utf-8', errors="ignore").rstrip()
        print(inline)

        dire = parse(inline)
        if not dire:
            return 0, {}

        north = dire.get("North", 0.0)
        south = dire.get("South", 0.0)
        west = dire.get("West", 0.0)
        east = dire.get("East", 0.0)

        # Debugging statements
        #print(f"North: {north}")
        #print(f"South: {south}")
        #print(f"West: {west}")
        #print(f"East: {east}")

        return [north, south, west, east]

def main():
    read_flex_data()

if __name__ == "__main__":
    main()
