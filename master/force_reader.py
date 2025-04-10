import serial
import time
import re

def extract_calibrated_angle_dict(data: str):
    """
    Extracts the most recent calibrated angle per direction from sensor output.

    Parameters:
        data (str): Raw string containing sensor output.

    Returns:
        dict: Dictionary with directions as keys and calibrated angles as float values.
    """
    # Clean data to avoid line break issues
    cleaned_data = data.replace('\n', ' ')

    # Regex: capture direction and calibrated angle
    pattern = r'\b(\w+)\s*\|\s*Raw Angle:.*?Calibrated Angle:\s*(-?[\d.]+)°'
    matches = re.findall(pattern, cleaned_data)

    # Create dict with most recent calibrated angle per direction
    angle_dict = {}
    for direction, angle in matches:
        angle_dict[direction] = float(angle)

    return angle_dict

def read_flex_data(port='COM3', baud_rate=9600):
    
    with serial.Serial(port, baud_rate) as arduino:
        time.sleep(2)
    
        start_time = time.perf_counter()
    
        arduino.reset_input_buffer()
            
        inline = arduino.readline().decode('utf-8', errors="ignore").rstrip()
            
        dire = extract_calibrated_angle_dict(inline)
            
        if not dire:
            return 0, {}
            
        north = dire["North"]
        south = dire["South"]
        west = dire["West"]
        east = dire["East"]
            
        #get time in between each loop
            
        cur_time = time.perf_counter()  # Get precise current time
        elapsed_time = (cur_time - start_time)
        start_time = cur_time;
        print(f"{elapsed_time:.6f} s")
        print(f"North {north}")
        print(f"South {south}")
        print(f"West {west}")
        print(f"East {east}")
    
        return elapsed_time, dire


def main():
    read_flex_data();

if __name__ == "__main__":
    main()
