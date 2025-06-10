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
        
        # Try to get supported channels
        try:
            supported_channels = imu.features().supportedChannelFields(mscl.MipTypes.CLASS_AHRS_IMU)
            print("\nSupported channels:")
            for ch in supported_channels:
                print(f"- {ch.channelField()}")
            log.write('\nSupported channels detected')
        except Exception as e:
            print(f"Warning: Could not get supported channels: {e}")
            log.write(f'\nWarning: Could not get supported channels: {e}')
        
        ahrs_channel_initialize(log, imu)
        
        print("Enabling data stream...")
        imu.enableDataStream(mscl.MipTypes.CLASS_AHRS_IMU)
        time.sleep(0.5)  # Give IMU time to process
        
        print("Resuming IMU...")
        imu.resume()
        time.sleep(0.5)  # Give IMU time to process
        
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
        uart_port = mscl.Connection.Serial("/dev/serial0", 115200)
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

def ahrs_channel_initialize(log, imu):
    try:
        print("Starting channel initialization...")
        ahrsImuChs = mscl.MipChannels()
        
        # Try with just accelerometer first
        print("Adding accelerometer channel...")
        ahrsImuChs.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_RAW_ACCEL_VEC, mscl.SampleRate.Hertz(500)))
        
        print("Setting active channel fields...")
        imu.setToIdle()  # Ensure we're in idle before changing channels
        time.sleep(0.5)
        
        imu.setActiveChannelFields(mscl.MipTypes.CLASS_AHRS_IMU, ahrsImuChs)
        print("IMU channels initialized")
        log.write('\n' + "IMU channels initialized")
    except mscl.Error as e:
        error_msg = f"MSCL Error in channel initialization: {str(e)}"
        print(error_msg)
        log.write('\n' + error_msg)
        raise
    except Exception as e:
        error_msg = f"Error in channel initialization: {str(e)}"
        print(error_msg)
        log.write('\n' + error_msg)
        raise

def poll_data(log, imu):
    try:
        packets = imu.getDataPackets(500)
        
        for packet in packets:
            descriptor = packet.descriptorSet()
            timestamp = packet.timestamp()
            
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
