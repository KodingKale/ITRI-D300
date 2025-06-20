import serial
import time
from datetime import datetime

def main(gnss_port = '/dev/ttyACM0',
         log_file = 'log.txt'):
    
    log = start_log(log_file)
    gnss = initialize_gnss(log, gnss_port)
    try:
        configure_gnss(gnss, log)
        log.close()
        rawx = open("./raws/rawx" + (datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")) + ".ubx", "w")
        read_gnss(gnss, rawx)
    except KeyboardInterrupt:
        pass
    finally:
        gnss.close()

def start_log(log_file):
    log = open(log_file, 'a')
    log.write('\n#################################################################\n')
    log.write(f"GNSS initialization started at {datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} \n")
    log.write('#################################################################\n')
    return log

def initialize_gnss(log, gnss_port):
    gnss = serial.Serial(
        port=gnss_port,
        baudrate=9600, 
        timeout=1)
    
    # Clear any leftover data
    gnss.reset_input_buffer()
    gnss.reset_output_buffer()
    
    print("GNSS initialized successfully")
    log.write("GNSS initialized successfully\n")
    return gnss

def configure_gnss(gnss, log):
    open_file = open("./configs/EVK-M8T-0-01.txt", "r")
    for line in open_file:
        line.strip()
        linesplit = line.split(" - ")
        action = "configuring: " + linesplit[0]
        print(action)
        log.write(action + "\n")
        bytestring = bytes([0xB5, 0x62])
        for byte in linesplit[1].split():
            bytestring += bytes([int(byte, 16)])
        checksum = fletcher_checksum(bytestring[2:])
        while gnss.out_waiting:
            pass
        gnss.write(bytestring + checksum)

def read_gnss(gnss, log):
    data = b''
    while True:
        data += gnss.read()
        if data[-2:] == b'\xb5\x62':
            data = data[:-2]
            if packet_validation(data, log):
                print(data)
                log.write(str(data))
            data = b'\xb5\x62'
        
def packet_validation(data, log):
    if data[0:2] != b'\xb5\x62':
        print("Invalid packet header: " + str(data[0:2]))
        log.write("Invalid packet header: " + str(data[0:2]) + "\n")
        return False
    if fletcher_checksum(data[2:-2]) != data[-2:]:
        print("Invalid checksum, expected: " + str(fletcher_checksum(data[2:-2])) + " but got: " + str(data[-2:]))
        log.write("Invalid checksum, expected: " + str(fletcher_checksum(data[2:-2])) + " but got: " + str(data[-2:]) + "\n")
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
