import serial

ser = serial.Serial('/dev/ttyACM0', 9600)
s = [0,1]
while True:
	read_serial = ser.readline()
	read_serial = read_serial.decode("utf-8")
	print(read_serial) # units is in grams
