#!/Users/QTM/Desktop/QualisysRobotiqSoftwareTrigger/robotiq_python_script/Script/activate.bat

import argparse
import os
import socket
import stat
import subprocess
import sys
import threading
from multiprocessing import Process, Value
from os.path import join
from pathlib import Path

import qtm_datastream

# shared memory var status_qtm: 0 = capture stopped; 1 = capture started
status_qtm = Value('d', 0)


class Server(object):
    def __init__(self, interface, port):
        self.interface = interface
        self.port = port
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.interface, self.port))

        while True:
            data, addr = sock.recvfrom(1024)
            # print('server', data)
            status_qtm.value = int(data)
            print('server', status_qtm.value)


def delete_last_line_of_file(fileobj):
    pos = fileobj.tell() - 1

    while pos > 0 and fileobj.read(1) != "\n":
        pos -= 1
        fileobj.seek(pos, os.SEEK_SET)
    pos -= 1

    if pos > 0:
        fileobj.seek(pos, os.SEEK_SET)
        fileobj.truncate()


def robotiq_data_logger(status_qtm, folder, file):
    counter = 1
    p_num = 0
    p = None

    current_dir = Path(__file__).parent.resolve()
    exec_path = join(current_dir, 'robotiq_python_script/pyFT300stream_2.py')

    target = f"python {exec_path}"

    while True:
        if status_qtm.value and p_num == 0:
            log = open(folder.joinpath(str(file) + str(counter) + '.txt'), 'w+')
            # p = subprocess.Popen(target, stdout=log, shell=False)
            # p = subprocess.Popen(["python", target])
            p = subprocess.Popen(target, stdout=log, shell=False)
            p_num = 1

        if not status_qtm.value and p_num == 1:
            p.terminate()
            p.wait()
            delete_last_line_of_file(log)
            log.close()
            p_num = 0
            counter += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir',
                        help='directory to store data',
                        required=True)
    parser.add_argument('-f', '--file',
                        help='filename',
                        required=True)
    args = parser.parse_args()

    folder = Path(args.dir)
    folder.mkdir(mode=0o777, parents=True, exist_ok=True)
    os.chmod(folder, stat.S_IWOTH)

    if any(folder.iterdir()):
        print("Please move existing data!")
        sys.exit()

    server = Server('127.0.0.1', 8888)
    qtm = Process(target=qtm_datastream.stream, daemon=True)
    qtm.start()

    robotiq = Process(target=robotiq_data_logger,
                      args=(status_qtm, folder, args.file),
                      daemon=True)
    robotiq.start()

    qtm.join()
