from typing import IO

from csv_logger import CsvLogger
from robotiq_python_script.handle_connector import HandleConnector, HandleDataPoint
import argparse


def print_header(file: IO):
    file.write('time,frequency,forceX,forceY,forceZ,torqueX,torqueY,torqueZ\n')


def print_data_point(file: IO, dp: HandleDataPoint):
    file.write(
        f'{dp.elapsed_time},{dp.frequency},{dp.force.x},{dp.force.y},{dp.force.z},{dp.torque.x},{dp.torque.y},{dp.torque.z}\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--left', type=str, default='/dev/ttyUSB1')
    parser.add_argument('--right', type=str, default='/dev/ttyUSB0')
    parser.add_argument('--output-left', type=str, required=True)
    parser.add_argument('--output-right', type=str, required=True)

    args = parser.parse_args()

    file_left = args.output_left
    file_right = args.output_right

    csv_logger = CsvLogger.create(args.left, args.right, file_left, file_right)
    csv_logger.start()
    csv_logger.join()


if __name__ == '__main__':
    main()
