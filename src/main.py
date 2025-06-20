from datetime import datetime
from configuration import main as configuration
from imu_datastream import main as imu_datastream
from gnss_datastream import main as gnss_datastream

gnss_port = 'COM8'
imu_port = '/dev/ttyS0'
gps_offset = [0.0, 0.0, 0.0] # [x,y,z]m
decimation = 0x01 # 1/decimation Hz (max 333.333 Hz)

def main():
    log_file = initalize_log()
    configuration(imu_port = imu_port, gnss_port = gnss_port, gps_offset = gps_offset, decimation = decimation, log_file = log_file)
    gnss_datastream(gnss_port = gnss_port, log_file = log_file)
    imu_datastream(imu_port = imu_port, log_file = log_file)

def initalize_log():
    log_file = "./logs/log"+ datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f') +".txt"
    log = open(log_file, 'a')
    log.write('\n#################################################################\n')
    log.write(f"Log started at {datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} \n")
    log.write('#################################################################\n')
    log.close()
    return log_file

if __name__ == "__main__":
    main()