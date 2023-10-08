import threading
from os.path import abspath
from typing import IO

from robotiq_python_script.handle_connector import HandleConnector, HandleDataPoint, Coordinate


class CsvPrinter:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.file = open(self.filename, 'w')
        self.stopped = False
        self.print_header()

    def print_header(self):
        self.file.write('time,frequency,forceX,forceY,forceZ,torqueX,torqueY,torqueZ,posixtime\n')
        self.file.flush()

    def print_data_point(self, dp: HandleDataPoint):
        self.file.write( 
            f'{dp.elapsed_time},{dp.frequency},{dp.force.x},{dp.force.y},{dp.force.z},{dp.torque.x},{dp.torque.y},{dp.torque.z},{dp.absolute_time}\n')
        self.file.flush()
        
    def stop(self):
        self.stopped = True
        self.file.close()
        
    def dispatch(self, hdp: HandleDataPoint):
        if not self.stopped:
            self.print_data_point(hdp)


class CsvLogger:
    def __init__(self, connector_right: HandleConnector, connector_left: HandleConnector, csv_printer_left: CsvPrinter,
                 csv_printer_right: CsvPrinter):
        self.connector_right = connector_right
        self.connector_left = connector_left
        self.csv_printer_left = csv_printer_left
        self.csv_printer_right = csv_printer_right

    def start(self):
        self.connector_left.start()
        self.connector_right.start()

    def stop(self):
        self.connector_left.teardown()
        self.connector_right.teardown()
        self.csv_printer_left.stop()
        self.csv_printer_right.stop()

    @staticmethod
    def create(left_port: str, right_port: str, filename_left: str, filename_right: str) -> 'CsvLogger':
        connector_right = HandleConnector(right_port)
        connector_left = HandleConnector(left_port)

        subscriber_left = CsvPrinter(abspath(filename_left))
        connector_left.subscribe(subscriber_left)

        subscriber_right = CsvPrinter(abspath(filename_right))
        connector_right.subscribe(subscriber_right)

        return CsvLogger(connector_right, connector_left, subscriber_left, subscriber_right)
