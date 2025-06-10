import serial
import time
import struct
from datetime import datetime

descriptor = {
    'Sensor': 0x80,
    'Acceleration': 0x04,
    'Gyroscope': 0x05,
    'Magnetometer': 0x06,
    'Velocity': 0x08,
    'GPS Timestamps': 0x12,
    'Temperature': 0x14,
    'Pressure': 0x17,
}


def main():
    #Make log file
    log = start_log()
    try:
        # Initialize IMU
        imu = initialize_imu()
        print("IMU initialized successfully")
        
        # Wait for sensor to stabilize
        time.sleep(0.5)
        
        poll_imu_acceleration(imu, log)
        
        # Continuous reading loop
        while True:
            data = read_imu_acceleration(imu, log)
            if data:  # Only print if we got valid data
                message = f"Acceleration: X={data['x']:.6f}, Y={data['y']:.6f}, Z={data['z']:.6f} g"
                print(message)
                log.write(message + '\n')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
        log.write("\nExiting...\n")
    finally:
        imu.close()
        log.close()
        
def initialize_imu():
    '''
    initialize UART port for 3DM-CV7-INS
    Default settings: 115200 baud, 8 data bits, 1 stop bit, no parity
    '''
    imu = serial.Serial(
        port='/dev/ttyS0',  # Primary UART on Raspberry Pi
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    
    # Clear any leftover data
    imu.reset_input_buffer()
    imu.reset_output_buffer()
    
    # Set to idle mode first
    idle_command = bytes([0x75, 0x65, 0x01, 0x02, 0x02, 0x06])
    checksum = fletcher_checksum(idle_command)
    imu.write(idle_command + checksum)
    time.sleep(0.1)
    
    # Resume current streaming
    stream_command = bytes([0x75, 0x65, 0x01, 0x02, 0x02, 0x06])
    checksum = fletcher_checksum(stream_command)
    imu.write(stream_command + checksum)
    time.sleep(0.1)
    
    return imu

'''
def parse_raw_data(raw_data, log):
    """
    Parse raw data and returns decoded values.
    raw_data: array of bytes containing IMU data
    returns: dictionary containing IMU data
    """
    if raw_data[0:2] != [0x75, 0x65]:
        raise ValueError("Invalid header")
    
    # Parse the data
'''

def parse_acceleration_data(raw_data, log):
    '''
    Parse acceleration data from the sensor using struct.
    MIP Packet Format:
    - First 2 bytes: Header (0x75 0x65)
    - Next bytes: Descriptor (0x80)
    - Next byte: Payload length (0x0E)
    Field:
    - Next bytes: Field Length (0x0E)
    - Next bytes: Field Descriptor (0x04)
    - Next 12 bytes: acceleration data (3 floats, 4 bytes each for x, y, z)
    Checksum:
    - Last 2 bytes: Checksum
    '''
    try:
        # Check if we have enough data
        if len(raw_data) < 20:
            print(f"Not enough data: {len(raw_data, log)} bytes")
            return None
            
        # Verify header
        if raw_data[0:2] != bytes([0x75, 0x65]):
            print(f"Invalid header: {raw_data[0:2].hex()}")
            return None
            
        # Extract acceleration data (12 bytes, 3 floats)
        # Using explicit little-endian format for float values
        accel_data = raw_data[6:18]
        accel_x, accel_y, accel_z = struct.unpack('>fff', accel_data)
        
        # Convert to g (if needed - depends on your sensor configuration)
        
        return {
            'x': accel_x,
            'y': accel_y,
            'z': accel_z
        }
    except Exception as e:
        print(f"Error parsing data: {e}")
        log.write(f"Error parsing data: {e}\n")
        return None

def poll_imu_acceleration(imu, log):
    command = bytes([0x75, 0x65, 0x0C, 0x06, 0x06, 0x0D, 0x80, 0x01, 0x01, 0x04])
    checksum = fletcher_checksum(command)
    command += checksum
    imu.write(command)

def read_imu_acceleration(imu, log):
    # Wait for minimum response size with timeout
    start_time = time.time()
    while imu.in_waiting < 20 and (time.time() - start_time) < 1.0:
        pass
    
    if imu.in_waiting < 20:
        print(f"Timeout waiting for data. Bytes available: {imu.in_waiting}")
        return None
        
    raw_data = imu.read(20)
    
    # Validate checksum
    if raw_data[18:20] != fletcher_checksum(raw_data[0:18]):  # Exclude sync bytes and checksum
        print(f'Checksum failed. Expected: {fletcher_checksum(raw_data[0:18]).hex()}, Got: {raw_data[18:20].hex()}')
        log.write(f'Checksum failed. Expected: {fletcher_checksum(raw_data[0:18]).hex()}, Got: {raw_data[18:20].hex()}\n')
        return None
        
    # Validate packet type
    if raw_data[2] != 0x80:
        print(f'Invalid descriptor set: 0x{raw_data[2]:02x}')
        log.write(f'Invalid descriptor set: 0x{raw_data[2]:02x}\n')
        return None
        
    # Validate field descriptor
    if raw_data[5] != 0x04:
        print(f'Invalid field descriptor: 0x{raw_data[5]:02x}')
        log.write(f'Invalid field descriptor: 0x{raw_data[5]:02x}\n')
        return None
        
    return parse_acceleration_data(raw_data, log)

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

def start_log():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    log = open('./logs/log.txt', 'a')
    log.write('\n#################################################################\n')
    log.write('Log started at ' + current_time + '\n')
    log.write('#################################################################\n')
    return log


if __name__ == '__main__':
    main()
