import serial
import time
import re
from threading import Thread

# Regex pattern to parse "Raw: 512  V: 2.502  %: 45.3"
pattern = re.compile(r"Raw:\s*(\d+)\s+V:\s*([\d.]+)\s+%:\s*([\d.]+)")

# Global latest sensor values
# Structure: (raw, voltage, percent)
latest_sheet = (0, 0.0, 0.0)

stop_flag = False  # for stopping the thread

def parse(data: str):
    """
    Parses a line from the Arduino conductive sheet sensor.
    
    Example input:
        "Raw: 512  V: 2.502  %: 45.3"
    
    Returns:
        dict: {"raw": int, "voltage": float, "percent": float}
    """
    match = pattern.search(data)
    if match:
        return {
            "raw": int(match.group(1)),
            "voltage": float(match.group(2)),
            "percent": float(match.group(3)),
        }
    return {}


def serial_loop(port='/dev/ttyACM0', baud_rate=115200):
    """ Continuously read serial and update latest_sheet """
    global latest_sheet, stop_flag
    try:
        with serial.Serial(port, baud_rate, timeout=0.01) as arduino:
            time.sleep(2)  # allow connection to settle
            while not stop_flag:
                inline = arduino.readline().decode('utf-8', errors="ignore").strip()
                if not inline:
                    continue
                parsed = parse(inline)
                if parsed:
                    latest_sheet = (
                        parsed["raw"],
                        parsed["voltage"],
                        parsed["percent"],
                    )
    except Exception as e:
        print(f"[Sheet Serial error] {e}")


def start_serial_thread(port='/dev/ttyACM0', baud_rate=115200):
    """ Start the serial reading thread """
    global stop_flag
    stop_flag = False
    thread = Thread(target=serial_loop, args=(port, baud_rate), daemon=True)
    thread.start()
    return thread


def get_latest_sheet():
    """ Get the most recent conductive sheet values (raw, voltage, percent) """
    return latest_sheet


def stop_serial_thread():
    """ Signal the serial loop to stop """
    global stop_flag
    stop_flag = True


# Optional quick test
if __name__ == "__main__":
    start_serial_thread()
    try:
        while True:
            print(get_latest_sheet())
            time.sleep(0.2)
    except KeyboardInterrupt:
        stop_serial_thread()
        print("Stopped.")
