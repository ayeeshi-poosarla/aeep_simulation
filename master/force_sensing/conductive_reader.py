import serial
import time
import re

def parse_sheet_data(data: str):
    """
    Parse a line from the Arduino conductive sheet sensor.

    Expected format:
        "Raw: 512  V: 2.502  %: 45.3"

    Returns:
        dict: {"raw": int, "voltage": float, "percent": float}
    """
    pattern = r"Raw:\s*(\d+)\s+V:\s*([\d.]+)\s+%:\s*([\d.]+)"
    match = re.search(pattern, data)
    if match:
        raw = int(match.group(1))
        voltage = float(match.group(2))
        percent = float(match.group(3))
        return {"raw": raw, "voltage": voltage, "percent": percent}
    return {"raw": 0, "voltage": 0.0, "percent": 0.0}


def read_sheet_data(port='/dev/ttyACM0', baud_rate=115200):
    """
    Connects to Arduino and reads one line of data from the conductive sheet sensor.

    Parameters:
        port (str): Serial port of Arduino (e.g., 'COM3' on Windows, '/dev/ttyACM0' on Linux).
        baud_rate (int): Baud rate for serial communication.

    Returns:
        tuple: (raw, voltage, percent) values. Defaults to zeros if parsing fails.
    """
    with serial.Serial(port, baud_rate) as arduino:
        time.sleep(2)  # wait for connection to establish
        inline = arduino.readline().decode('utf-8', errors="ignore").strip()
        parsed = parse_sheet_data(inline)
        return parsed["raw"], parsed["voltage"], parsed["percent"]


def main():
    """
    Example loop to continuously read and print conductive sheet values.
    """
    try:
        while True:
            raw, voltage, percent = read_sheet_data()
            print(f"Raw={raw}, Voltage={voltage:.3f} V, Percent={percent:.1f}%")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
