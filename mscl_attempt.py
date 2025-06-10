import mscl
from datetime import datetime
import time  # Added for delays

def main():
    log = start_log()
    try:
        imu = imu_initialize(log)
        
        # Add debug info about the IMU
        print(f"IMU Model: {imu.modelName()}")
        print(f"IMU Serial: {imu.serialNumber()}")
        log.write(f'\nIMU Model: {imu.modelName()}')
        log.write(f'\nIMU Serial: {imu.serialNumber()}')
        
        success = imu.ping()
        if not success:
            raise Exception("Failed to ping IMU")
        
        print("Ping successful, setting to idle...")
        imu.setToIdle()
        time.sleep(0.5)  # Give IMU time to process
        
        # Configure IMU settings
        print("\nConfiguring IMU settings...")
        imuChannels = mscl.MipChannels()
        
        # Add accelerometer data - using the correct channel field for CV7
        imuChannels.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_SCALED_ACCEL_VEC, mscl.SampleRate.Hertz(100)))
        
        # Set the active channels
        print("Setting active channel fields...")
        imu.setActiveChannelFields(mscl.MipTypes.CLASS_AHRS_IMU, imuChannels)
        
        # Set to streaming mode
        print("Setting communication mode...")
        imu.enableDataStream(mscl.MipTypes.CLASS_AHRS_IMU)
        
        print("Starting data streaming...")
        imu.resume()
        
        try:
            while True:
                poll_data(log, imu)
        except KeyboardInterrupt:
            print("\nExiting...")
            log.write("\nExiting...\n")
            imu.setToIdle()
    except Exception as e:
        print(f"Error in main: {str(e)}")
        log.write(f'\nError in main: {str(e)}')
    finally:
        log.close()

def imu_initialize(log):
    try:
        uart_port = mscl.Connection.Serial("/dev/ttyS0", 115200)
        imu = mscl.InertialNode(uart_port)
        
        # Try to communicate with the device
        if not imu.ping():
            raise Exception("Initial ping failed")
            
        # Set to idle before any configuration
        imu.setToIdle()
        time.sleep(0.5)
        
        print("IMU initialized")
        log.write('\n' + "IMU initialized")
        return imu
    except Exception as e:
        error_msg = f"IMU initialization failed: {str(e)}"
        print(error_msg)
        log.write('\n' + error_msg)
        raise

def poll_data(log, imu):
    try:
        packets = imu.getDataPackets(500)
        
        for packet in packets:
            timestamp = packet.deviceTimestamp()
            points = packet.data()
            for dataPoint in points:
                data_str = f"Time: {timestamp}, Descriptor: {descriptor}, Data: {dataPoint.as_Vector()}"
                print(data_str)
                log.write('\n' + data_str)
    except Exception as e:
        print(f"Error polling data: {str(e)}")
        log.write(f'\nError polling data: {str(e)}')

def start_log():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
	
    print('log started')
    log = open('./logs/log.txt', 'a')
    log.write('\n#################################################################\n')
    log.write('Log started at ' + current_time + '\n')
    log.write('#################################################################\n')
    return log




































if __name__ == '__main__':
    main()
