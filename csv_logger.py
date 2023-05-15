import threading
from typing import IO

from robotiq_python_script.handle_connector import HandleConnector, HandleDataPoint, Coordinate


class CsvLogger:
    def __init__(self, connector_right: HandleConnector, connector_left: HandleConnector, filename_left: str,
                 filename_right: str):
        self.filename_right = filename_right
        self.filename_left = filename_left
        self.connector_right = connector_right
        self.connector_left = connector_left
        self.do_run = True

    def print_header(self, file: IO):
        file.write('time,frequency,forceX,forceY,forceZ,torqueX,torqueY,torqueZ\n')

    def print_data_point(self, file: IO, dp: HandleDataPoint):
        file.write(
            f'{dp.elapsed_time},{dp.frequency},{dp.force.x},{dp.force.y},{dp.force.z},{dp.torque.x},{dp.torque.y},{dp.torque.z}\n')

    def _run(self):
        gen_left = self.connector_left.read()
        gen_right = self.connector_right.read()

        with open(self.filename_left, 'w+') as f_left:
            with open(self.filename_right, 'w+') as f_right:
                self.print_header(f_left)
                self.print_header(f_right)

                while self.do_run:
                    left: HandleDataPoint = next(gen_left)
                    right: HandleDataPoint = next(gen_right)

                    self.print_data_point(f_left, left)
                    self.print_data_point(f_right, right)

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def join(self):
        self.thread.join()

    def stop(self):
        self.do_run = False

    @staticmethod
    def create(left_port: str, right_port: str, filename_left: str, filename_right: str):
        connector_right = HandleConnector(right_port)
        connector_left = HandleConnector(left_port)

        connector_left.setup()
        connector_right.setup()

        return CsvLogger(connector_right, connector_left, filename_left, filename_right)
