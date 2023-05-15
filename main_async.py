from typing import IO

from robotiq_python_script.handle_connector import HandleConnector, HandleDataPoint
import argparse


def print_header(file: IO):
    file.write('time,frequency,forceX,forceY,forceZ,torqueX,torqueY,torqueZ\n')


def print_data_point(file: IO, dp: HandleDataPoint):
    file.write(
        f'{dp.elapsed_time},{dp.frequency},{dp.force.x},{dp.force.y},{dp.force.z},{dp.torque.x},{dp.torque.y},{dp.torque.z}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--left', type=str, default='/dev/ttyUSB1')
    parser.add_argument('--right', type=str, default='/dev/ttyUSB0')
    parser.add_argument('--output-left', type=str, required=True)
    parser.add_argument('--output-right', type=str, required=True)

    args = parser.parse_args()

    file_left = args.output_left
    file_right = args.output_right

    connector_right = HandleConnector(args.right)
    connector_left = HandleConnector(args.left)

    connector_left.setup()
    connector_right.setup()

    gen_left = connector_left.read()
    gen_right = connector_right.read()

    with open(file_left) as f_left:
        with open(file_right) as f_right:
            print_header(f_left)
            print_header(f_right)

            while True:
                left: HandleDataPoint = next(gen_left)
                right: HandleDataPoint = next(gen_right)

                print_data_point(f_left, left)
                print_data_point(f_right, right)


if __name__ == '__main__':
    main()
