import smbus
from time import sleep
#dt03
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

def MPU_Init():
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	bus.write_byte_data(Device_Address, CONFIG, 0)
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)
	
def read_raw_data(addr):
	high = bus.read_byte_data(Device_Address, addr)
	low = bus.read_byte_data(Device_Address, addr+1)
	value = ((high << 8) | low)
	
	if(value>32768):
		value = value - 65536
	return value
	
bus = smbus.SMBus(1)
Device_Address = 0x68

MPU_Init()

print("Reading Data of Gyroscope and Accelerometer")
i = 0
while i < 10:
	acc_x = read_raw_data(ACCEL_XOUT_H)
	acc_y = read_raw_data(ACCEL_YOUT_H)
	acc_z = read_raw_data(ACCEL_ZOUT_H)
	
	gyro_x = read_raw_data(GYRO_XOUT_H)
	gyro_y = read_raw_data(GYRO_YOUT_H)
	gyro_z = read_raw_data(GYRO_ZOUT_H)
	
	Ax = acc_x/16384.0
	Ay = acc_y/16384.0
	Az = acc_z/16384.0
	
	Gx = gyro_x/131.0
	Gy = gyro_y/131.0
	Gz = gyro_z/131.0
	
	f = open("accelgyro.txt", "a")
	result = ("Gx=%.2f%s/s\tGy=%.2f%s/s\tGz=%.2f%s/s\tAx=%.2f g\tAy=%.2f g\tAz=%.2f g\n" %
          (Gx, u'\u00b0', Gy, u'\u00b0', Gz, u'\u00b0', Ax, Ay, Az))
	f.write(result)
	print(result)
	f.close()
	i += 1
	sleep(1)