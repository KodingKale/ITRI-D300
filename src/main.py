from datetime import datetime
from inu_datastream import main as inu_datastream
from gnss_configuration import main as gnss_configuration

gnss_port = 'COM8'
imu_port = '/dev/ttyS0'
gps_offset = [0.0, 0.0, 0.0] # [x,y,z]m
decimation = 0x01 # 1/decimation Hz (max 333.333 Hz)

def main():
    log_file = initalize_log()
    gnss_configuration(gnss_port = gnss_port, log_file = log_file)
    inu_datastream(imu_port = imu_port, gps_offset = gps_offset, decimation = decimation, log_file = log_file)

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