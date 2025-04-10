import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

#define the pin that goes into circuit
pin_to_circuit = 4

def rc_time (pin_to_circuit):
	count = 0
	
	#output on the pin for
	GPIO.setup(pin_to_circuit, GPIO.OUT)
	GPIO.output(pin_to_circuit, GPIO.LOW)
	time.sleep(0.1)
	
	#change the pin back to input
	GPIO.setup(pin_to_circuit, GPIO.IN)
	
	#count until the pin goes high
	while (GPIO.input(pin_to_circuit) == GPIO.LOW):
		count += 1
		
	return count
	
#catch when script is interrupted, clean up correctly
try:
	#main loop
	while True:
		print(rc_time(pin_to_circuit))

except KeyboardInterrupt:
	pass
	
finally:
	GPIO.cleanup()
	
