import serial
import time
from datetime import datetime

def is_port_busy(port_name):
    try:
        with serial.Serial(port_name) as s:
            return False  # Port is available
    except serial.SerialException:
        return True  # Port is busy

def main(gnss_port = '/dev/ttyACM0',
         log_file = 'log.txt'):
    
    log = start_log(log_file)
    try:
        if is_port_busy(gnss_port):
            print(f"Port {gnss_port} is busy. Please check if another program is using it.")
            log.write(f"Port {gnss_port} is busy. Please check if another program is using it.\n")
            return
            
        gnss = initialize_gnss(log, gnss_port)
        configure_gnss(gnss, log)
    except KeyboardInterrupt:
        print("\nExiting...")
        log.write("\nExiting...\n")
        gnss.close()
    finally:
        log.close()

# ... existing code ... 