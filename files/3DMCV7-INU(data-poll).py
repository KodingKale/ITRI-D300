import serial
import time
import struct
from datetime import datetime

imu_port = 'COM7'
gps_offset = [0.0, 0.0, 0.0] # [x, y, z] in meters

def main():
    #Make log file
    log = start_log()
    try:
        # Initialize IMU
        imu = initialize_imu(log)
        initialize_pps(imu, log)
        initialize_gps(imu, log)
        time.sleep(0.5)
        imu.reset_output_buffer()
        imu.reset_input_buffer()
        imu.read_until(b'\x75\x65')

        # Continuous reading loop
        while True:
            poll_data(imu, log)
            data = read_data(imu, log)
            if data:  # Only print if we got valid data
                message = f"Acceleration: X={data['x']:.6f}, Y={data['y']:.6f}, Z={data['z']:.6f} m/s^2 Time of Week: {data['time_of_week']:.6f}, Week Number: {data['week_number']}"
                print(message)
                log.write(message + '\n')
    except KeyboardInterrupt:
        print("\nExiting...")
        log.write("\nExiting...\n")
        imu.close()
    finally:
        log.close()
        
########################################################################## functions ##########################################################################
def start_log():
    """
    Start a new log file with a timestamp
    """
    log = open('./logs/log' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt', 'w')
    log.write('\n#################################################################\n')
    log.write(f'Log started at {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')} \n')
    log.write('#################################################################\n')
    return log

def initialize_imu(log):
    '''
    initialize UART port for 3DM-CV7-INS
    Default settings: 115200 baud, 1s timeout
    '''
    imu = serial.Serial(
        port=imu_port,
        baudrate=115200,
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
    return imu

def initialize_pps(imu, log):
    """
    Initialize PPS on GPIO3 (1 Hz 25 ms)
    """
    imu.write(bytes([0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x03, 0x02, 0x01, 0x00, 0x3C, 0x6D]))
    ack = imu.read(10)
    print("PPS initialized succesfully")
    log.write("PPS initialized succesfully\n")

def initialize_gps(imu, log):
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
    ack = imu.read(10)
    #Configure UART
    imu.write(bytes([0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x04, 0x05, 0x21, 0x00, 0x60, 0xBA]))
    imu.write(bytes([0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x02, 0x05, 0x22, 0x00, 0x5F, 0xB4]))
    imu.write(bytes([0x75, 0x65, 0x01, 0x08, 0x08, 0x09, 0x01, 0x02, 0x00, 0x01, 0xC2, 0x00, 0xBA, 0x3B]))

def poll_data(imu, log):
    """
    Poll data from IMU
    """
    imu.write(bytes([0x75, 0x65, 0x0C, 0x07, 0x07, 0x0D, 0x80, 0x01, 0x02, 0xD3, 0x04, 0x5B, 0x50]))
    

def read_data(imu, log):
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




























if __name__ == '__main__':
    main()