
# -*- coding: utf-8 -*-
"""
Created on 2021-01-04
This is a simple example showing of to get measurement data1 of FT300 in stream mode using python.
Hardward preparation:
---------------------
The ft300_1 have to be connected to the PC via USB and power with a 24V power supply.
Dependencies:
*************
MinimalModbus: https://pypi.org/project/MinimalModbus/
@author: Benoit CASTETS
"""
######################
#Libraries importation
######################
import time
from math import *
import serial
import minimalmodbus as mm
import io
import libscrc

######################
#Functions
######################

def forceFromSerialMessage(serialMessage,zeroRef=[0,0,0,0,0,0]):
  """Return a list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] correcponding to the dataArray1

  Parameters
  ----------
  serialMessage:
    bytearray which contents the serial message send by the FT300.
    [0x20,0x4e,LSBdata1,MSBdata2,...,LSBdata6,MSBdata6,crc1,crc2]
    Check FT300 manual for details.
  zeroRef:
    list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] use the set the zero reference of the sensor.

  Return
  ------
  forceTorque:
    list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] correcponding to the dataArray1
  """
  #Initialize variable
  forceTorque=[0,0,0,0,0,0]

  #converte bytearray values to integer. Apply the zero offset and round at 2 decimals
  forceTorque[0]=round(int.from_bytes(serialMessage[2:4], byteorder='little', signed=True)/100-zeroRef[0],2)
  forceTorque[1]=round(int.from_bytes(serialMessage[4:6], byteorder='little', signed=True)/100-zeroRef[1],2)
  forceTorque[2]=round(int.from_bytes(serialMessage[6:8], byteorder='little', signed=True)/100-zeroRef[2],2)
  forceTorque[3]=round(int.from_bytes(serialMessage[8:10], byteorder='little', signed=True)/1000-zeroRef[3],2)
  forceTorque[4]=round(int.from_bytes(serialMessage[10:12], byteorder='little', signed=True)/1000-zeroRef[4],2)
  forceTorque[5]=round(int.from_bytes(serialMessage[12:14], byteorder='little', signed=True)/1000-zeroRef[5],2)

  return forceTorque

def crcCheck(serialMessage):
  """Check if the serial message have a valid CRC.

  Parameters
  -----------
  serialMessage:
    bytearray which contents the serial message send by the FT300.
    [0x20,0x4e,LSBdata1,MSBdata2,...,LSBdata6,MSBdata6,crc1,crc2]
    Check FT300 manual for details.

  Return
  ------
  checkResult:
    bool, return True if the message have a valid CRC and False if not.
  """
  checkResult = False

  #CRC from serial message
  crc = int.from_bytes(serialMessage[14:16], byteorder='little', signed=False)
  #calculated CRC
  crcCalc = libscrc.modbus(serialMessage[0:14])

  if crc == crcCalc:
    checkResult = True

  return checkResult


#############################
#Serial connection parameters
#############################

#Communication setup
BAUDRATE=19200
BYTESIZE=8
PARITY="N"
STOPBITS=1
TIMEOUT=1

#Change PORTNAME1 according the port on which is connected the FT300

#For Ubuntu
############
#Name of the port (string) where is connected the gripper. Usually
#/dev/ttyUSB0 on Linux. It is necesary to allow permission to access
#this connection using the bash command sudo chmod 666 /dev/ttyUSB0

#For windows
############
#Check the name of the port using robotiq user interface. It should be something
#like: COM12

PORTNAME1="COM3"
PORTNAME2="COM4"

#Set the slave ID of the gripper. By default it is 9.

SLAVEADDRESS=9

#####################################################################################################
#Main program
#####################################################################################################

if __name__ == '__main__':

  try:
    ############################
    #Desactivate streaming mode
    ############################


    #To stop the data1 stream, communication must be interrupted by sending a series of 0xff characters to the Sensor. Sending for about
    #0.5s (50 times)will ensure that the Sensor stops the stream.
    ser1=serial.Serial(port=PORTNAME1, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)
    ser2=serial.Serial(port=PORTNAME2, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)
    packet = bytearray()
    sendCount=0
    while sendCount<50:
      packet.append(0xff)
      sendCount=sendCount+1
    ser1.write(packet)
    ser2.write(packet)
    ser1.close()
    ser2.close()
    del packet
    del sendCount
    del ser1
    del ser2


    ############################
    #Activate streaming mode
    ############################


    #Setup minimalmodbus
    ####################

    #Communication setup
    mm.BAUDRATE=BAUDRATE
    mm.BYTESIZE=BYTESIZE
    mm.PARITY=PARITY
    mm.STOPBITS=STOPBITS
    mm.TIMEOUT=TIMEOUT

    #Create FT300 object
    ft300_1=mm.Instrument(PORTNAME1, slaveaddress=SLAVEADDRESS)
    ft300_2=mm.Instrument(PORTNAME2, slaveaddress=SLAVEADDRESS)
    ft300_1.close_port_after_each_call=True
    ft300_2.close_port_after_each_call=True

    #Uncomment to see binary messages for debug
    #ft300_1.debug=True
    #ft300_1.mode=mm.MODE_RTU

    #Write 0x0200 in 410 register to start streaming
    ###############################################
    registers1=ft300_1.write_register(410,0x0200)
    registers2=ft300_2.write_register(410,0x0200)

    del ft300_1
    del ft300_2

    ############################
    #Open serial connection
    ############################


    ser1=serial.Serial(port=PORTNAME1, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)
    ser2=serial.Serial(port=PORTNAME2, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)
    startTime=time.time()


    ############################
    #Initialize stream reading
    ############################

    #Bytes use to itendify the beginning of the serial message
    STARTBYTES = bytes([0x20,0x4e])

    #Read serial buffer until founding the bytes [0x20,0x4e]
    #First serial reading.
    #This message in uncomplete in most cases so it is ignored.
    data1 = ser1.read_until(STARTBYTES)
    data2 = ser2.read_until(STARTBYTES)


    #Second serial reading.
    #This message is use to make the zero of the sensor.
    data1 = ser1.read_until(STARTBYTES)
    data2 = ser2.read_until(STARTBYTES)
    #convert from byte to bytearray
    dataArray1 = bytearray(data1)
    dataArray2 = bytearray(data2)
    #Delete the end bytes [0x20,0x4e] and place it at the beginning of the bytearray
    dataArray1 = STARTBYTES+dataArray1[:-2]
    dataArray2 = STARTBYTES+dataArray2[:-2]
    #Check if the serial message have a valid CRC
    if crcCheck(dataArray1) is False:
      raise Exception("CRC ERROR: Serial message and the CRC does not match")
    if crcCheck(dataArray2) is False:
      raise Exception("CRC ERROR: Serial message and the CRC does not match")

    #Save sensor value force and torue value in a variable which will be use as a zero reference
    #The FT300 is suppose to be at rest when starting this program.
    zeroRef1 = forceFromSerialMessage(dataArray1)
    zeroRef2 = forceFromSerialMessage(dataArray2)


    #Program variables
    ##################

    #Number of received messages
    nbrMessages = 0
    #data1 rate frequency in Hz
    frequency = 0

    # print("time(s),freq(Hz),Fx,Fy,Fz,Tx,Ty,Tz\n")
    print("time(s),freq(Hz),"+"Fx_"+PORTNAME1+","+"Fy_"+PORTNAME1+","+\
          "Fz_"+PORTNAME1+","+"Tx_"+PORTNAME1+","+"Ty_"+PORTNAME1+","+\
          "Tz_"+PORTNAME1+","+"Fx_"+PORTNAME2+","+"Fy_"+PORTNAME2+","+\
          "Fz_"+PORTNAME2+","+"Tx_"+PORTNAME2+","+"Ty_"+PORTNAME2+","+\
          "Tz_"+PORTNAME2+"\n")
    while True:
      #Read serial message
      ####################

      data1 = ser1.read_until(STARTBYTES)
      data2 = ser2.read_until(STARTBYTES)
      #convert from byte to bytearray
      dataArray1 = bytearray(data1)
      dataArray2 = bytearray(data2)
      #Delete the end bytes [0x20,0x4e] and place it at the beginning of the bytearray
      dataArray1 = STARTBYTES+dataArray1[:-2]
      dataArray2 = STARTBYTES+dataArray2[:-2]

      #calulate force and torque form serial message
      #############################################
      forceTorque1=forceFromSerialMessage(dataArray1,zeroRef1)
      forceTorque2=forceFromSerialMessage(dataArray2,zeroRef2)

      #CRC validation
      ################
      if crcCheck(dataArray1) is False:
        raise Exception("CRC ERROR: Serial message and the CRC does not match")
      if crcCheck(dataArray2) is False:
        raise Exception("CRC ERROR: Serial message and the CRC does not match")

      #Frequency
      ###############
      #Update message counter
      nbrMessages+=1
      #Update timer
      elapsedTime=time.time()-startTime
      #Calculate average frequency
      frequency=round(nbrMessages/elapsedTime)

      #data1 printing
      ###############
      print(str(elapsedTime)+","+str(frequency)+","+str(forceTorque1)[1:-1]+","+str(forceTorque2)[1:-1])
      # print("F: ",frequency,"Hz - force Vector : ",forceTorque)

  except KeyboardInterrupt:
    print("Program ended")
    ser1.close()
    pass
