import serial
import time

ser = serial.Serial('/dev/serial0')
print(ser.name)
print(ser.is_open)
ser.write(b'hello')
ser.close()
