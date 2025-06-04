import serial
import time

def test_uart_connections():
    # Configure UART0 (typically /dev/ttyAMA0)
    try:
        uart0 = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        print("UART0 initialized successfully")
    except Exception as e:
        print(f"Error initializing UART0: {e}")
        return

    # Configure UART1 (typically /dev/ttyAMA1)
    try:
        uart1 = serial.Serial(
            port='/dev/ttyAMA1', 
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        print("UART1 initialized successfully")
    except Exception as e:
        print(f"Error initializing UART1: {e}")
        return

    # Test sending and receiving on both UARTs
    test_message = b"Test Message"
    
    # Test UART0
    print("\nTesting UART0...")
    try:
        uart0.write(test_message)
        response = uart0.readline()
        print(f"UART0 sent: {test_message}")
        print(f"UART0 received: {response}")
    except Exception as e:
        print(f"Error testing UART0: {e}")

    # Test UART1
    print("\nTesting UART1...")
    try:
        uart1.write(test_message)
        response = uart1.readline()
        print(f"UART1 sent: {test_message}")
        print(f"UART1 received: {response}")
    except Exception as e:
        print(f"Error testing UART1: {e}")

    # Close the connections
    uart0.close()
    uart1.close()

if __name__ == "__main__":
    test_uart_connections()
