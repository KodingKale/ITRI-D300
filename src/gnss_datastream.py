import serial
import time
from datetime import datetime

def main(gnss_port = '/dev/ttyACM0',
         log_file = 'log.txt'):
    
    gnss = initialize_gnss(log_file, gnss_port)
    try:
        rawx = open("./rawx/rawx" + log_file[10:-4] + ".ubx", "w")
        read_gnss(gnss, rawx)
    except KeyboardInterrupt:
        pass
    finally:
        gnss.close()

def initialize_gnss(log, gnss_port):
    gnss = serial.Serial(
        port=gnss_port,
        baudrate=9600, 
        timeout=1)
    
    # Clear any leftover data
    gnss.reset_input_buffer()
    gnss.reset_output_buffer()
    
    return gnss

def read_gnss(gnss, rawx):
    data = b''
    while True:
        data += gnss.read()
        if data[-2:] == b'\xb5\x62':
            data = data[:-2]
            if packet_validation(data, rawx):
                print(data)
                rawx.write(str(data))
            data = b'\xb5\x62'
        
def packet_validation(data, rawx):
    if data[0:2] != b'\xb5\x62':
        print("Invalid packet header: " + str(data[0:2]))
        rawx.write("Invalid packet header: " + str(data[0:2]) + "\n")
        return False
    if fletcher_checksum(data[2:-2]) != data[-2:]:
        print("Invalid checksum, expected: " + str(fletcher_checksum(data[2:-2])) + " but got: " + str(data[-2:]))
        rawx.write("Invalid checksum, expected: " + str(fletcher_checksum(data[2:-2])) + " but got: " + str(data[-2:]) + "\n")
        return False
    return True

def fletcher_checksum(data):
    '''
    Calculate Fletcher checksum for 3DM-CV7-INS
    data: bytes object containing the message to checksum
    Returns: 2 bytes checksum
    '''
    MSB = 0
    LSB = 0
    for byte in data:
        MSB = (MSB + byte) & 0xFF  # Ensure 8-bit result using & 0xFF
        LSB = (LSB + MSB) & 0xFF
    # Return the two checksum bytes
    return(bytes([MSB, LSB])) 
