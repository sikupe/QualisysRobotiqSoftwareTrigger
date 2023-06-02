import os
import stat
import sys
from multiprocessing import Process
from pathlib import Path

import qtm_datastream
from csv_logger import CsvLogger
from main import Server


class QTMLogger:
    def __init__(self, qtm: Process, robotiq: CsvLogger):
        self.qtm = qtm
        self.robotiq = robotiq

    def start(self):
        self.server = Server('127.0.0.1', 8888)
        self.qtm.start()
        self.robotiq.start()

    def stop(self):
        self.qtm.terminate()
        self.robotiq.stop()
        self.server.stop()

    @staticmethod
    def create(folder: str, left_com: str, right_com: str, file_left: str, file_right: str):
        folder = Path(folder)
        folder.mkdir(mode=0o777, parents=True, exist_ok=True)
        os.chmod(folder, stat.S_IWOTH)

        if any(folder.iterdir()):
            print("Please move existing data!")
            sys.exit()
        qtm = Process(target=qtm_datastream.stream, daemon=True)

        robotiq = CsvLogger.create(left_com, right_com, file_left, file_right)

        return QTMLogger(qtm, robotiq)