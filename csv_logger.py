import threading
from os.path import abspath
from typing import IO

from robotiq_python_script.handle_connector import HandleConnector, HandleDataPoint, Coordinate


class CsvLogger:
    def __init__(self, connector_right: HandleConnector, connector_left: HandleConnector, filename_left: str,
                 filename_right: str):
        self.filename_right = abspath(filename_right)
        self.filename_left = abspath(filename_left)
        self.connector_right = connector_right
        self.connector_left = connector_left
        self.do_run = True

    def print_header(self, file: IO):
        file.write('time,frequency,forceX,forceY,forceZ,torqueX,torqueY,torqueZ,posixtime\n')

    def print_data_point(self, file: IO, dp: HandleDataPoint):
        file.write(
            f'{dp.elapsed_time},{dp.frequency},{dp.force.x},{dp.force.y},{dp.force.z},{dp.torque.x},{dp.torque.y},{dp.torque.z},{dp.absolute_time}\n')

    def _run(self, connector, filename):
        try:
            gen = connector.read()

            with open(filename, 'w') as f:
                self.print_header(f)

                while self.do_run:
                    hdp: HandleDataPoint = next(gen)

                    self.print_data_point(f, hdp)
        finally:
            connector.teardown()
    def start(self):
        self.thread_left = threading.Thread(target=self._run, args=(self.connector_left, self.filename_left))
        self.thread_left.start()
        self.thread_right = threading.Thread(target=self._run, args=(self.connector_right, self.filename_right))
        self.thread_right.start()

    def join(self):
        self.thread_left.join()
        self.thread_right.join()

    def stop(self):
        self.do_run = False

    @staticmethod
    def create(left_port: str, right_port: str, filename_left: str, filename_right: str) -> 'CsvLogger':
        connector_right = HandleConnector(right_port)
        connector_left = HandleConnector(left_port)

        connector_left.start()
        connector_right.start()

        return CsvLogger(connector_right, connector_left, filename_left, filename_right)
