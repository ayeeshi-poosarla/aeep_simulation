import serial
import time
import re


def parse(line):
    pattern_accel = re.compile(r'Accel X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+) m/s\^2')
    pattern_gyro = re.compile(r'Gyro X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)radians/s')
    pattern_mag = re.compile(r'Mag X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)uT')

    
    match_accel = pattern_accel.search(line)
    if match_accel:
        ax = float(match_accel.group(1))
        ay = float(match_accel.group(2))
        az = float(match_accel.group(3))

    match_gyro = pattern_gyro.search(line)
    if match_gyro:
        gx = float(match_gyro.group(1))
        gy = float(match_gyro.group(2))
        gz = float(match_gyro.group(3))
    
    match_mag = pattern_mag.search(line)
    if match_mag:
        mx = float(match_mag.group(1))
        my = float(match_mag.group(2))
        mz = float(match_mag.group(3))

    return ax, ay, az, gx, gy, gz, mx, my, mz

def printlst(lst):
    for e in lst:
        print(e)

def read_imu_data(port='COM6', baud_rate=115200, num_samples=50):
    with serial.Serial(port, baud_rate) as arduino:
        time.sleep(2)
        start_time = time.perf_counter()
        
        arduino.reset_input_buffer()
        
        inline = arduino.readline().decode('utf-8', errors="ignore").rstrip()
        
        ax, ay, az, gx, gy, gz, mx, my, mz = parse(inline)
        
        cur_time = time.perf_counter()  # Get precise current time
        elapsed_time = (cur_time - start_time)  # Convert to milliseconds
        start_time = cur_time;
        
        
        out = [elapsed_time, ax, ay, az, gx, gy, gz, mx, my, mz];
        
        #For debugging
        #printlst(out)
        
        return out
        
        

    
def main():
    read_imu_data();

if __name__ == "__main__":
    main()
