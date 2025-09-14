import serial
import time
import re

pattern = re.compile(r"(\w+):\s*(-?\d+(?:\.\d+)?)")

def parse(data: str):
    matches = pattern.findall(data)
    return {d: float(v) for d, v in matches}

def read_flex_data(ser):
    """Read one line from an open Serial object and return R,MB,MM,MT,L."""
    while True:
        raw = ser.readline().decode("utf-8", errors="ignore").strip()
        if not raw:
            continue
        #print(raw);
        vals = parse(raw)
        if vals:       # got something valid
            return (
                vals.get("North", 0.0),
                vals.get("South", 0.0),
                vals.get("West", 0.0),
                vals.get("East", 0.0),          
            )


def main():
    try:
        with serial.Serial("/dev/ttyACM0", 115200, timeout=1) as ser:
            time.sleep(2)  # let Arduino reboot
            while True:
                angles = read_flex_data(ser)
                print(angles)
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
