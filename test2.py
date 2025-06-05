import serial
import time

ser = serial.Serial('/dev/serial1')
print(ser.name)
print(ser.is_open)
x = ser.read(5)
print(x)
ser.close()
