import serial
import time
import struct
from datetime import datetime

def main(imu_port = '/dev/ttyS0',
        gnss_port = '/dev/ttyACM0',
        gps_offset = [0.0, 0.0, 0.0], 
        decimation = 0x01, 
        log_file = 'log.txt'):
    
    # Initialize GNSS
    log = start_log(log_file)
    gnss = initialize_gnss(log, gnss_port)
    configure_gnss(gnss, log)
    gnss.close()

    #Initialize IMU
    imu = initialize_imu(log, imu_port)
    initialize_pps(imu, log)
    initialize_gps(imu, log, gps_offset)
    initialize_stream(imu, log, decimation)
    imu.close()
    log.close()
    
def start_log(log_file):
    log = open(log_file, 'a')
    return log

def initialize_gnss(log, gnss_port):
    log.write('\n#################################################################\n')
    log.write(f"GNSS initialization started at {datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} \n")
    log.write('#################################################################\n')
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
        
def start_log(log_file):
    """
    Start a new log file with a timestamp
    """
    log = open(log_file, 'a')

def initialize_imu(log, imu_port):
    '''
    initialize UART port for 3DM-CV7-INS
    Default settings: 115200 baud, 8 data bits, 1 stop bit, no parity
    '''
    log.write('\n#################################################################\n')
    log.write(f"IMU initialization started at {datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} \n")
    log.write('#################################################################\n')
    
    imu = serial.Serial(
        port=imu_port,
        baudrate = 115200,
        timeout=1
    )
    
    # Clear any leftover data
    imu.reset_input_buffer()
    imu.reset_output_buffer()
    
    # Set to idle mode first
    idle_command = bytes([0x75, 0x65, 0x01, 0x02, 0x02, 0x02])
    checksum = fletcher_checksum(idle_command)
    imu.write(idle_command + checksum)
    ack = imu.read(10)
    print("IMU initialized successfully")
    log.write("IMU initialized succesfully\n")
    command = bytes([0x75, 0x65, 0x01, 0x08, 0x08, 0x09, 0x01, 0x01, 0x00, 0x07, 0x08, 0x00])
    command += fletcher_checksum(command)
    imu.write(command)
    time.sleep(0.25)
    imu.close()
    imu = serial.Serial(
        port=imu_port,
        baudrate = 460800,
        timeout=1
    )
    return imu

def initialize_pps(imu, log):
    """
    Initialize PPS on GPIO3 (1 Hz 25 ms)
    """
    pps_source = bytes([0x75, 0x65, 0x0C, 0x04, 0x04, 0x28, 0x01, 0x03])
    pps_source += fletcher_checksum(pps_source)
    imu.write(pps_source)
    imu.write(bytes([0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x03, 0x02, 0x01, 0x00, 0x3C, 0x6D]))
    print("PPS initialized succesfully")
    log.write("PPS initialized succesfully\n")

def initialize_gps(imu, log, gps_offset):
    """
    Initialize GPS at given offset
    """ 
    #TODO: Fill out
    #Set GPS offset
    command = bytes([0x75, 0x65, 0x0D, 0x0F, 0x0F, 0x13, 0x01])
    command += struct.pack('>f', gps_offset[0])
    command += struct.pack('>f', gps_offset[1])
    command += struct.pack('>f', gps_offset[2])
    command += fletcher_checksum(command)
    imu.write(command)
    #Configure UART
    imu.write(bytes([0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x02, 0x05, 0x22, 0x00, 0x5F, 0xB4]))
    imu.write(bytes([0x75, 0x65, 0x01, 0x08, 0x08, 0x09, 0x01, 0x02, 0x00, 0x01, 0xC2, 0x00, 0xBA, 0x3B]))
    time.sleep(0.25)
    print("GPS initialized successfully")
    log.write("GPS initialized sucessfully") 

def initialize_stream(imu, log, decimation):
    """
    Initialize stream of timestamps and acceleration data
    """
    
    command = bytes([0x75, 0x65, 0x0C, 0x0B, 0x0B, 0x0F, 0x01, 0x80, 0x02, 0xD3, 0x00, decimation, 0x04, 0x00, decimation])
    command += fletcher_checksum(command)
    imu.write(command)
    imu.write(bytes([0x75, 0x65, 0x0C, 0x05, 0x05, 0x0F, 0x01, 0x82, 0x00, 0x82, 0x13]))
    imu.write(bytes([0x75, 0x65, 0x0C, 0x05, 0x05, 0x0F, 0x01, 0x94, 0x00, 0x94, 0x37]))
    imu.write(bytes([0x75, 0x65, 0x0C, 0x05, 0x05, 0x0F, 0x01, 0xA0, 0x00, 0xA0, 0x4F]))
    imu.write(bytes([0x75, 0x65, 0x13, 0x04, 0x04, 0x1F, 0x01, 0x01, 0x16, 0x61]))
    time.sleep(0.25)
    print("Stream initialized successfully")
    log.write("Stream initialized successfully\n")

    #Resume stream
    imu.write(bytes([0x75, 0x65, 0x01, 0x02, 0x02, 0x06, 0xE5, 0xCB]))

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
