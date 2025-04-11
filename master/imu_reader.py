import serial
import time
import re

def parse(line):
    """Helper function used to parse line from Arduino and find values."""

    import re

    # Initialize patterns
    pattern_accel = re.compile(r'Accel X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+) m/s\^2')
    pattern_gyro = re.compile(r'Gyro X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+) radians/s')
    pattern_mag = re.compile(r'Mag X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+) uT')

    # Initialize all values
    ax = ay = az = gx = gy = gz = mx = my = mz = None

    # Parse acceleration
    match_accel = pattern_accel.search(line)
    if match_accel:
        ax = float(match_accel.group(1))
        ay = float(match_accel.group(2))
        az = float(match_accel.group(3))

    # Parse gyroscope
    match_gyro = pattern_gyro.search(line)
    if match_gyro:
        gx = float(match_gyro.group(1))
        gy = float(match_gyro.group(2))
        gz = float(match_gyro.group(3))

    # Parse magnetometer
    match_mag = pattern_mag.search(line)
    if match_mag:
        mx = float(match_mag.group(1))
        my = float(match_mag.group(2))
        mz = float(match_mag.group(3))

    # Ensure all values were found
    if None in [ax, ay, az, gx, gy, gz, mx, my, mz]:
        raise ValueError("Could not parse all IMU data from line.")

    return ax, ay, az, gx, gy, gz, mx, my, mz

"""Helper function used to print out values of a list and verify outputs"""
def printlst(lst):
    for e in lst:
        print(e)

"""Function opens connection to arduino nano port and collects data from the IMU"""
def read_imu_data(port='/dev/ttyACMO', baud_rate=115200):
    #Open up arduino nano connection
    with serial.Serial(port, baud_rate) as arduino:
        time.sleep(2)
        
        arduino.reset_input_buffer()
        
        #Take in new line
        inline = arduino.readline().decode('utf-8', errors="ignore").rstrip()
        #print(inline)
        
        ax, ay, az, gx, gy, gz, mx, my, mz = parse(inline)

        out = [ax, ay, az, gx, gy, gz, mx, my, mz]
        
        #For debugging
        #printlst(out)
        
        #return list of 9 values
        return out
        
        

    
def main():
    read_imu_data()

if __name__ == "__main__":
    main()
