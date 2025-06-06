import serial
import time
import struct

descriptor = {
    'Sensor' : 0x80,
    'Acceleration' : 0x04,
    'Gyroscope' : 0x05,
    'Magnetometer' : 0x06,
    'Velocity' : 0x08,
    'GPS Timestamps' : 0x12
    'Temperature' : 0x14,
    'Pressure' : 0x17,
}

def main():
    # Initialize IMU
    imu = initialize_imu()
    # Continuous reading loop
    while True:
        data = read_imu_data(imu)
        print(f"Acceleration: X={data['x']:.2f}, Y={data['y']:.2f}, Z={data['z']:.2f} m/s²")
        time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if 'imu' in locals():
            imu.close()









*/functions
def initialize_imu():
    '''
    initialize UART port for 3DM-CV7-INS
    Default settings: 115200 baud, 8 data bits, 1 stop bit, no parity
    '''
    imu = serial.Serial(
        port='/dev/serial0',  # Primary UART on Raspberry Pi
        baudrate=115200,
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
    imu.write(command)
    while imu.inWaiting() < 20:
        pass
    raw_data = imu.read(20)
    return parse_acceleration_data(raw_data)






if __name__ == '__main__':
    main()

