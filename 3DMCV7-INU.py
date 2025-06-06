import serial
import time
import struct

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
    try:
        # Initialize IMU
        imu = initialize_imu()
        print("IMU initialized successfully")
        
        # Continuous reading loop
        while True:
            data = read_imu_acceleration(imu)
            if data:
                print(f"Acceleration: X={data['x']:.2f}, Y={data['y']:.2f}, Z={data['z']:.2f} m/s²")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        imu.close()
        
def initialize_imu():
    '''
    initialize UART port for 3DM-CV7-INS
    Default settings: 115200 baud, 8 data bits, 1 stop bit, no parity
    '''
    imu = serial.Serial(
        port='/dev/serial0',  # Primary UART on Raspberry Pi
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    # Clear any leftover data
    imu.reset_input_buffer()
    imu.reset_output_buffer()
    return imu

'''
def parse_raw_data(raw_data):
    """
    Parse raw data and returns decoded values.
    raw_data: array of bytes containing IMU data
    returns: dictionary containing IMU data
    """
    if raw_data[0:2] != [0x75, 0x65]:
        raise ValueError("Invalid header")
    
    # Parse the data
'''

def parse_acceleration_data(raw_data):
    '''
    Parse acceleration data from the sensor using struct.
    Header: 
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
    # Check if we have enough data (minimum 16 bytes for this example)
    if len(raw_data) < 20:
        raise ValueError("Not enough data to parse acceleration")
        
    # Unpack three 4-byte floats (acceleration x, y, z)
    # Starting from byte 3 (after header and length)
    # '<' means little-endian, 'fff' means three 32-bit floats
    accel_x, accel_y, accel_z = struct.unpack('fff', raw_data[6:18])
        
    return {
        'x': accel_x,
        'y': accel_y,
        'z': accel_z
    }

def read_imu_acceleration(imu):
    command = struct.pack('B'*10, 0x75, 0x65, 0x0C, 0x06, 0x06, 0x0D, 0x80, 0x01, 0x01, 0x04)
    checksum = fletcher_checksum(command)
    command += checksum
    imu.write(command)
    while imu.inWaiting() < 20:
        pass
    raw_data = imu.read(20)
    return parse_acceleration_data(raw_data)

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
    return(struct.pack('BB', LSB, MSB)) 


def main():
    try:
        # Initialize IMU
        imu = initialize_imu()
        print("IMU initialized successfully")
        
        # Continuous reading loop
        while True:
            data = read_imu_acceleration(imu)
            if data:
                print(f"Acceleration: X={data['x']:.2f}, Y={data['y']:.2f}, Z={data['z']:.2f} m/s²")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        imu.close()

if __name__ == '__main__':
    main()

