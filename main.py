import subprocess
import os, sys, time, inspect, socket, threading, stat
from multiprocessing import Process, Value
import qtm_datastream
from pathlib import Path
from subprocess import Popen, PIPE, CalledProcessError
from threading  import Thread
import signal
import argparse



#shared memory var status_qtm: 0 = capture stopped; 1 = capture started
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
            #print('server', data)
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
    line = None
    target = 'C:/Users/QTM/Desktop/gabriel/RobotiqForceTorque300/FT-300_dev_package_SDP-1.0.1_20180328/driverSensor_modified.exe'

    while True:
        if status_qtm.value and p_num == 0:
            log = open(folder.joinpath(str(file) + str(counter) + '.txt'), 'w+')
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
