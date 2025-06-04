import serial
import time

def main():
    
    # Initialize UART ports
    uart0 = serial.Serial(port='/dev/serial0', baudrate=9600)
    uart1 = serial.Serial(port='/dev/serial1', baudrate=9600)
    
    # Clear any leftover data
    uart0.reset_input_buffer()
    uart0.reset_output_buffer()
    uart1.reset_input_buffer()
    uart1.reset_output_buffer()

    # Send and receive messages
    uart0.write(b'Message from UART0\n')
    time.sleep(0.1)
    response0 = uart1.readline()
    uart1.write(b'Message from UART1\n')
    time.sleep(0.1)
    response1 = uart0.readline()

    print(f"UART0 response: {response0}")
    print(f"UART1 response: {response1}")

    uart0.close()
    uart1.close()

if __name__ == '__main__':
    main()
