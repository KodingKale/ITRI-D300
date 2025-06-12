import serial
import time
import struct

def initialize_imu():
    # Initialize UART port for 3DM-CV7-INS
    # Default settings: 115200 baud, 8 data bits, 1 stop bit, no parity
    imu = serial.Serial(
        port='/dev/serial0',  # Primary UART on Raspberry Pi
        baudrate=115200,
        timeout=1
    )
    
    # Clear any leftover data
    imu.reset_input_buffer()
    imu.reset_output_buffer()
    return imu

def parse_acceleration_data(raw_data):
    """
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
    """
    # Check if we have enough data (minimum 16 bytes for this example)
    if len(raw_data) < 20:
        return None
        
    # Unpack three 4-byte floats (acceleration x, y, z)
    # Starting from byte 3 (after header and length)
    # '<' means little-endian, 'fff' means three 32-bit floats
    accel_x, accel_y, accel_z = struct.unpack('<fff', raw_data[6:18])
        
    return {
        'x': accel_x,
        'y': accel_y,
        'z': accel_z
    }



*// Stop  point

def read_imu_data(imu):
    try:
        
        # Request acceleration data packet
        # Example command format using struct to pack the request
        # Header (0x75 0x65), Descriptor (0x0C), Length (0x02), Payload (0x01 0x02), CRC (0xE1)
        command = struct.pack('BBBBBB', 0x75, 0x65, 0x0C, 0x02, 0x01, 0x02)
        # Calculate CRC (simplified example)
        crc = sum(command) & 0xFF
        command += struct.pack('B', crc)
        
        # Send command
        imu.write(command)
        
        # Wait for response
        time.sleep(0.1)
        
        if imu.in_waiting >= 20:
            response = imu.read(20)
            # Parse the acceleration data
            accel_data = parse_acceleration_data(response)
            return accel_data
        return None
        
    except Exception as e:
        print(f"Error reading IMU: {e}")
        return None

def main():
    # Initialize IMU
    imu = initialize_imu()
    # Continuous reading loop
    while True:
        data = read_imu_data(imu)
        if data:
            print(f"Acceleration: X={data['x']:.2f}, Y={data['y']:.2f}, Z={data['z']:.2f} m/s²")
        time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if 'imu' in locals():
            imu.close()

if __name__ == '__main__':
    main()

