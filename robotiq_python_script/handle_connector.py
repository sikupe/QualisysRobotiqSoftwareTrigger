import time
from dataclasses import dataclass
from queue import Queue
from typing import Optional

import serial
import minimalmodbus as mm
import libscrc
import threading


@dataclass()
class Coordinate:
    x: float
    y: float
    z: float


@dataclass()
class HandleDataPoint:
    elapsed_time: float
    frequency: float
    force: Coordinate
    torque: Coordinate


class HandleConnector:
    def __init__(self, port_name: str, slave_address=9, baud_rate=19200, byte_size=8, parity="N", stop_bits=1,
                 timeout=1):
        """
        #############################
        # Serial connection parameters
        #############################

        # Communication setup

        # Change portname according the port on which is connected the FT300

        # For Ubuntu
        ############
        # Name of the port (string) where is connected the gripper. Usually
        # /dev/ttyUSB0 on Linux. It is necesary to allow permission to access
        # this connection using the bash command sudo chmod 666 /dev/ttyUSB0

        # For windows
        ############
        # Check the name of the port using robotiq user interface. It should be something
        # like: COM12
        Set the slave ID of the gripper. By default it is 9.
        """
        self.port_name = port_name
        self.slave_address = slave_address
        self.baud_rate = baud_rate
        self.byte_size = byte_size
        self.parity = parity
        self.stop_bits = stop_bits
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.thread: Optional[threading.Thread] = None
        self.queue = Queue()

    def setup(self):
        ############################
        # Deactivate streaming mode
        ############################

        # To stop the data stream, communication must be interrupted by sending a series of 0xff characters to the Sensor. Sending for about
        # 0.5s (50 times)will ensure that the Sensor stops the stream.
        ser = serial.Serial(port=self.port_name, baudrate=self.baud_rate, bytesize=self.byte_size, parity=self.parity,
                            stopbits=self.stop_bits,
                            timeout=self.timeout)
        packet = bytearray()
        send_count = 0
        while send_count < 50:
            packet.append(0xff)
            send_count = send_count + 1
        ser.write(packet)
        ser.close()
        del packet
        del send_count
        del ser

        ############################
        # Activate streaming mode
        ############################

        # Setup minimalmodbus
        ####################

        # Communication setup
        mm.BAUDRATE = self.baud_rate
        mm.BYTESIZE = self.byte_size
        mm.PARITY = self.parity
        mm.STOPBITS = self.stop_bits
        mm.TIMEOUT = self.timeout

        # Create FT300 object
        ft300 = mm.Instrument(self.port_name, slaveaddress=self.slave_address)
        ft300.close_port_after_each_call = True

        # Uncomment to see binary messages for debug
        # ft300.debug=True
        # ft300.mode=mm.MODE_RTU

        # Write 0x0200 in 410 register to start streaming
        ###############################################
        registers = ft300.write_register(410, 0x0200)

        del ft300

        ############################
        # Open serial connection
        ############################

        self.serial = serial.Serial(port=self.port_name, baudrate=self.baud_rate, bytesize=self.byte_size,
                                    parity=self.parity,
                                    stopbits=self.stop_bits,
                                    timeout=self.timeout)

        self.thread = threading.Thread(target=self._start_read_async)
        self.thread.start()

    def _start_read_async(self):
        start_time = time.time()

        ############################
        # Initialize stream reading
        ############################

        # Bytes use to itendify the beginning of the serial message
        start_bytes = bytes([0x20, 0x4e])

        # Read serial buffer until founding the bytes [0x20,0x4e]
        # First serial reading.
        # This message in uncomplete in most cases so it is ignored.
        data = self.serial.read_until(start_bytes)

        # Second serial reading.
        # This message is use to make the zero of the sensor.
        data = self.serial.read_until(start_bytes)
        # convert from byte to bytearray
        data_array = bytearray(data)
        # Delete the end bytes [0x20,0x4e] and place it at the beginning of the bytearray
        data_array = start_bytes + data_array[:-2]
        # Check if the serial message have a valid CRC
        if self.crc_check(data_array) is False:
            raise Exception("CRC ERROR: Serial message and the CRC does not match")

        # Save sensor value force and torue value in a variable which will be use as a zero reference
        # The FT300 is suppose to be at rest when starting this program.
        zero_ref = self.force_from_serial_message(data_array)

        # Program variables
        ##################

        # Number of received messages
        nbr_messages = 0
        # Data rate frequency in Hz
        frequency = 0

        while True:
            # Read serial message
            ####################

            data = self.serial.read_until(start_bytes)
            # convert from byte to bytearray
            data_array = bytearray(data)
            # Delete the end bytes [0x20,0x4e] and place it at the beginning of the bytearray
            data_array = start_bytes + data_array[:-2]

            # calculate force and torque form serial message
            #############################################
            force_torque = self.force_from_serial_message(data_array, zero_ref)

            # CRC validation
            ################
            if self.crc_check(data_array) is False:
                raise Exception("CRC ERROR: Serial message and the CRC does not match")

            # Frequency
            ###############
            # Update message counter
            nbr_messages += 1
            # Update timer
            elapsed_time = time.time() - start_time
            # Calculate average frequency
            frequency = round(nbr_messages / elapsed_time)

            data_point = HandleDataPoint(elapsed_time, frequency,
                                         Coordinate(force_torque[0], force_torque[1], force_torque[2]),
                                         Coordinate(force_torque[3], force_torque[4], force_torque[5]))

            self.queue.put(data_point)

    def read(self):
        while True:
            yield self.queue.get()

    def teardown(self):
        self.serial.close()

    @staticmethod
    def force_from_serial_message(serial_message, zero_ref=[0, 0, 0, 0, 0, 0]):
        """Return a list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] correcponding to the dataArray

        Parameters
        ----------
        serial_message:
          bytearray which contents the serial message send by the FT300.
          [0x20,0x4e,LSBdata1,MSBdata2,...,LSBdata6,MSBdata6,crc1,crc2]
          Check FT300 manual for details.
        zero_ref:
          list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] use the set the zero reference of the sensor.

        Return
        ------
        forceTorque:
          list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] correcponding to the dataArray
        """
        # Initialize variable
        force_torque = [0, 0, 0, 0, 0, 0]

        # convert bytearray values to integer. Apply the zero offset and round at 2 decimals
        force_torque[0] = round(
            int.from_bytes(serial_message[2:4], byteorder='little', signed=True) / 100 - zero_ref[0],
            2)
        force_torque[1] = round(
            int.from_bytes(serial_message[4:6], byteorder='little', signed=True) / 100 - zero_ref[1],
            2)
        force_torque[2] = round(
            int.from_bytes(serial_message[6:8], byteorder='little', signed=True) / 100 - zero_ref[2],
            2)
        force_torque[3] = round(
            int.from_bytes(serial_message[8:10], byteorder='little', signed=True) / 1000 - zero_ref[3],
            2)
        force_torque[4] = round(
            int.from_bytes(serial_message[10:12], byteorder='little', signed=True) / 1000 - zero_ref[4], 2)
        force_torque[5] = round(
            int.from_bytes(serial_message[12:14], byteorder='little', signed=True) / 1000 - zero_ref[5], 2)

        return force_torque

    @staticmethod
    def crc_check(serial_message):
        """Check if the serial message have a valid CRC.

        Parameters
        -----------
        serial_message:
          bytearray which contents the serial message send by the FT300.
          [0x20,0x4e,LSBdata1,MSBdata2,...,LSBdata6,MSBdata6,crc1,crc2]
          Check FT300 manual for details.

        Return
        ------
        checkResult:
          bool, return True if the message have a valid CRC and False if not.
        """
        check_result = False

        # CRC from serial message
        crc = int.from_bytes(serial_message[14:16], byteorder='little', signed=False)
        # calculated CRC
        crc_calc = libscrc.modbus(serial_message[0:14])

        if crc == crc_calc:
            check_result = True

        return check_result
