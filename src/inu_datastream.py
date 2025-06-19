import serial
import time
import struct
from datetime import datetime



def main(imu_port = '/dev/ttyS0',
         gps_offset = [0.0, 0.0, 0.0], 
         decimation = 0x03,
         log_file = 'log.txt'):
    
    log = start_log(log_file)
    imu = initialize_imu(log, imu_port)
    try:
        # Initialize IMU
        initialize_pps(imu, log)
        initialize_gps(imu, log, gps_offset)
        initialize_stream(imu, log, decimation)
        sync_stream(imu, log)

        # Continuous reading loop
        while True:
            data = read_stream_data(imu, log)
            if data:  # Only print if we got valid data
                message = f"Acceleration: X={data['x']:.6f}, Y={data['y']:.6f}, Z={data['z']:.6f} m/s^2 Time of Week: {data['time_of_week']:.6f}, Week Number: {data['week_number']}"
                print(message)
                log.write(message + '\n')
    except KeyboardInterrupt:
        print("\nExiting IMU...")
        log.write("\nExiting IMU...\n")
    finally:
        imu.close()
        log.close()
        
########################################################################## functions ##########################################################################
def start_log(log_file):
    """
    Start a new log file with a timestamp
    """
    log = open(log_file, 'a')
    log.write('\n#################################################################\n')
    log.write(f"IMU initialization started at {datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} \n")
    log.write('#################################################################\n')
    return log

def initialize_imu(log, imu_port):
    '''
    initialize UART port for 3DM-CV7-INS
    Default settings: 115200 baud, 8 data bits, 1 stop bit, no parity
    '''
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


def sync_stream(imu, log):
    """
    Sync stream by purging until header is found
    """
    time.sleep(0.5)
    imu.reset_input_buffer()
    imu.reset_output_buffer()
    while True:
        data = imu.read(1)
        if data == bytes([0x75]):
            if imu.read(1) == bytes([0x65]):
                imu.read(32)
                break
    print("Stream synced")
    log.write("Stream synced\n")
    pass

def read_stream_data(imu, log):
    """
    Read stream data from IMU and checks the validity of the data
    """
    # Wait for minimum response size with timeout
    raw_data = imu.read(34)
    
    # Validate checksum
    if raw_data[32:] != fletcher_checksum(raw_data[0:32]):
        print(f'Checksum failed. Expected: {fletcher_checksum(raw_data[0:32]).hex()}, Got: {raw_data[32:].hex()}')
        log.write(f'Checksum failed. Expected: {fletcher_checksum(raw_data[0:32]).hex()}, Got: {raw_data[32:].hex()}\n')
        return None
        
    # Validate packet type
    if raw_data[2] != 0x80:
        print(f'Invalid descriptor set: 0x{raw_data[2]:02x}')
        log.write(f'Invalid descriptor set: 0x{raw_data[2]:02x}\n')
        return None
        
    # Validate field descriptor
    if raw_data[5] != 0xD3 or raw_data[19] != 0x04:
        print(f'Invalid field descriptor: 0x{raw_data[5]:02x} or 0x{raw_data[19]:02x}')
        log.write(f'Invalid field descriptor: 0x{raw_data[5]:02x} or 0x{raw_data[19]:02x}\n')
        return None
        
    # Verify header
    if raw_data[0:2] != bytes([0x75, 0x65]):
        print(f"Invalid header: {raw_data[0:2]}")
        log.write(f"Invalid header: {raw_data[0:2]}\n")
        return None
    
    return parse_stream_data(raw_data, log)

def parse_stream_data(raw_data, log):
    '''
    Parse timestamp and acceleration data from the stream returning a dictionary with all the values
    '''
    try:
        # Check if we have enough data
        if len(raw_data) < 34:
            print(f"Not enough data: {len(raw_data)} bytes")
            return None
            
            
        gps_data = raw_data[6:18]
        time_of_week = struct.unpack('>d', raw_data[6:14])[0]
        week_number = struct.unpack('>H', raw_data[14:16])[0]


        accel_data = raw_data[20:32]
        accel_x, accel_y, accel_z = struct.unpack('>fff', accel_data)
        
        accel_x = accel_x * 9.80665
        accel_y = accel_y * 9.80665
        accel_z = accel_z * 9.80665

        # Convert acceleration data to m/s^2
        return {
            'time_of_week': time_of_week,
            'week_number': week_number,
            'x': accel_x,
            'y': accel_y,
            'z': accel_z
        }
    except Exception as e:
        print(f"Error parsing data: {e}")
        log.write(f"Error parsing data: {e}\n")
        return None

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
