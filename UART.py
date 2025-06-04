import serial
import time

def test_uart_connections():
    # Configure UART0 (Primary UART)
    try:
        uart0 = serial.Serial(
            port='/dev/serial0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
            exclusive=True  # Request exclusive access to the port
        )
        # Clear any leftover data
        uart0.reset_input_buffer()
        uart0.reset_output_buffer()
        print("UART0 initialized successfully")
    except Exception as e:
        print(f"Error initializing UART0: {e}")
        return

    # Configure UART1
    try:
        uart1 = serial.Serial(
            port='/dev/ttyUSB0',  # Secondary UART port on Raspberry Pi
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
            exclusive=True
        )
        # Clear any leftover data
        uart1.reset_input_buffer()
        uart1.reset_output_buffer()
        print("UART1 initialized successfully")
    except Exception as e:
        print(f"Error initializing UART1: {e}")
        uart0.close()
        return

    # Test sending and receiving on both UARTs
    test_message = b"Test Message\0"
    
    # Test UART0
    print("\nTesting UART0...")
    try:
        # Clear buffers before sending
        uart0.reset_input_buffer()
        uart0.reset_output_buffer()
        
        # Send data
        uart0.write(test_message)
        uart0.flush()  # Ensure all data is written
        time.sleep(0.1)  # Wait for transmission
        
        # Read response
        response = uart0.read_until(b'\0')  # Read until newline
        print(f"UART0 sent: {test_message}")
        print(f"UART0 received: {response}")
    except Exception as e:
        print(f"Error testing UART0: {e}")

    # Test UART1
    print("\nTesting UART1...")
    try:
        # Clear buffers before sending
        uart1.reset_input_buffer()
        uart1.reset_output_buffer()
        
        # Send data
        uart1.write(test_message)
        uart1.flush()  # Ensure all data is written
        time.sleep(0.1)  # Wait for transmission
        
        # Read response
        response = uart1.read_until(b'\0')  # Read until newline
        print(f"UART1 sent: {test_message}")
        print(f"UART1 received: {response}")
    except Exception as e:
        print(f"Error testing UART1: {e}")

    # Close the connections
    uart0.close()
    uart1.close()

if __name__ == "__main__":
    test_uart_connections()
