import mscl
from datetime import datetime

def main():
    log = start_log()
    imu = imu_initialize(log)
    success = imu.ping()
    imu.setToIdle()
    ahrs_channel_initialize(log, imu)
    imu.enableDataStream(mscl.MipTypes.CLASS_AHRS_IMU)
    imu.resume()
    try:
        while True:
            poll_data(log, imu)
    except KeyboardInterrupt:
        print("\nExiting...")
        log.write("\nExiting...\n")


def imu_initialize(log):
    uart_port = mscl.Connection.Serial("/dev/ttyS0", 115200)
    imu = mscl.IntertialNode(uart_port)
    print("IMU initialized")
    log.write('\n' + "IMU initialized")
    return imu

def ahrs_channel_initialize(log, imu):
    ahrsImuChs = mscl.MipChannels()
    ahrsImuChs.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_RAW_ACCEL_VEC, mscl.SampleRate.Hertz(500)))
    imu.setActiveChannelFields(mscl.MipTypes.CLASS_AHRS_IMU, ahrsImuChs)
    print("IMU channels initialized")
    log.write('\n' + "IMU channels initialized")


def poll_data(log, imu):
    packets = imu.getDataPackets(500)

    for packet in packets:
        packet.descriptorSet()  # the descriptor set of the packet
        packet.timestamp()      # the PC time when this packet was received

        # get all of the points in the packet
        points = packet.data()

        for dataPoint in points:
            print(dataPoint.as_Vector())
            log.write('\n' + dataPoint.as_Vector())





def start_log():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    log = open('./logs/log.txt', 'a')
    log.write('\n#################################################################\n')
    log.write('Log started at ' + current_time + '\n')
    log.write('#################################################################\n')
    return log




































if __name__ == ' __main__' :
    main()