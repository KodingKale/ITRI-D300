import serial
import serial.tools.list_ports
import time

def list_com_ports():
    """List all available COM ports"""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No COM ports found!")
        return []
    
    print("\nAvailable COM ports:")
    for port in ports:
        print(f"- {port.device}: {port.description}")
    return ports

def initialize_serial(port_name, baud_rate=115200):
    """Initialize serial port with given parameters"""
    try:
        ser = serial.Serial(
            port=port_name,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"\nSuccessfully opened {port_name}")
        print(f"Port settings:")
        print(f"- Baud rate: {ser.baudrate}")
        print(f"- Data bits: {ser.bytesize}")
        print(f"- Parity: {ser.parity}")
        print(f"- Stop bits: {ser.stopbits}")
        return ser
    except serial.SerialException as e:
        print(f"\nError opening {port_name}: {e}")
        return None

def test_serial_communication(ser):
    """Test reading and writing to serial port"""
    if not ser:
        return
    
    try:
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        while True:
            # Send test command
            test_cmd = bytes([0x75, 0x65, 0x01, 0x02, 0x02, 0x02])  # Example command
            print(f"\nSending: {test_cmd.hex()}")
            ser.write(test_cmd)
            
            # Wait for response
            time.sleep(0.1)
            
            if ser.in_waiting:
                response = ser.read(ser.in_waiting)
                print(f"Received: {response.hex()}")
            else:
                print("No response received")
            
            # Wait before next test
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except serial.SerialException as e:
        print(f"\nSerial error: {e}")
    finally:
        ser.close()
        print("\nSerial port closed")

def main():
    # List available ports
    ports = list_com_ports()
    if not ports:
        return
    
    # Let user select port
    print("\nSelect COM port to use:")
    for i, port in enumerate(ports):
        print(f"{i+1}: {port.device} - {port.description}")
    
    try:
        choice = int(input("Enter number (or 0 to quit): "))
        if choice == 0:
            return
        if 1 <= choice <= len(ports):
            selected_port = ports[choice-1].device
        else:
            print("Invalid choice")
            return
    except ValueError:
        print("Invalid input")
        return
    
    # Initialize selected port
    ser = initialize_serial(selected_port)
    if not ser:
        return
    
    # Run communication test
    print("\nStarting communication test...")
    print("Press Ctrl+C to stop")
    test_serial_communication(ser)

if __name__ == "__main__":
    main() 