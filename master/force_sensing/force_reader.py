import serial
import time
import re

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


def read_flex_data(port='COM3', baud_rate=9600):
    """
    Connects to the Arduino over serial, reads one line of data from flex sensors,
    and extracts angle information for each direction.

    Parameters:
        port (str): The COM port the Arduino is connected to (default 'COM3').
        baud_rate (int): The communication speed for serial transmission (default 9600).

    Returns:
        tuple: A 4-element tuple of angles (north, south, west, east) as floats. 
               If parsing fails, all values default to 0.0.
    """
    # Open the serial port
    with serial.Serial(port, baud_rate) as arduino:
        # Allow time for connection to establish
        time.sleep(2)
        
        # Read one line from the serial port, decode it, and strip whitespace
        inline = arduino.readline().decode('utf-8', errors="ignore").rstrip()

        # Parse the line to get a dictionary of direction-angle pairs
        dire = parse(inline)

        # If no valid data, return default zeroes
        if not dire:
            return 0.0, 0.0, 0.0, 0.0

        # Retrieve angles for each direction, defaulting to 0.0 if not found
        #north = dire.get("North", 0.0)
        #south = dire.get("South", 0.0)
        #west = dire.get("West", 0.0)
        #east = dire.get("East", 0.0)

        return dire


def main():
    """
    Main function to test reading from the flex sensor.
    Modify this function to loop, log, or display data as needed.
    """
    try:
        n, s, w, e = read_flex_data()
        print(f"North: {n}°\nSouth: {s}°\nWest: {w}°\nEast: {e}°")
    except Exception as err:
        print(f"Error reading flex data: {err}")


if __name__ == "__main__":
    main()
