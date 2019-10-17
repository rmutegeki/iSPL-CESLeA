"""
Contains utilities for data collection including sockets
"""

import datetime
import socket
import sys

'''    Simple socket server using threads
        Declare your socket variables here
'''
HOST = '192.168.137.1'  # Symbolic name, meaning all available interfaces
PORT = 5500  # Arbitrary non-privileged port

dt = datetime.datetime.now()

# The name of the file storing our data for this session
RAW_DATA_FILE = f"data/raw_data_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}"
with open(RAW_DATA_FILE + ".txt", "w") as file:
    file.write("timestamp, user, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, "
               "lacc_x, lacc_y, lacc_z, eul_x, eul_y, eul_z")
    file.write("\n")

# List all Settings/Configs from the WITHROBOT Sensor
ID = 0
ACC_X, ACC_Y, ACC_Z = 1, 2, 3
GYRO_X, GYRO_Y, GYRO_Z = 4, 5, 6
LACC_X, LACC_Y, LACC_Z, = 7, 8, 9
EUL_X, EUL_Y, EUL_Z = 10, 11, 12
COUNT = 1
USER = 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('Socket created')
    # Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print(f'Bind failed. Error Code : {msg[0]} Message: {msg[1]}')
        sys.exit()
    print('Socket bind complete')

    # Become a server socket, maximum 10 connections
    s.listen(10)
    print('Socket now listening')

    while True:
        # Wait to accept a connection - blocking call
        connection, address = s.accept()
        print(f'Connected with {address[0]}:{address[1]}')
        with connection:
            # Now keep talking with the client
            while True:
                try:
                    sensorData = connection.recv(1024)
                    timestamp = datetime.datetime.now().time()
                    if len(sensorData) > 0:
                        dataArray = sensorData.split(b',')  # Split the IMU String into an array called dataArray
                        if len(dataArray) < EUL_Z:
                            break
                        else:
                            sensorID = int(dataArray[ID])
                            acc_x, acc_y, acc_z = float(dataArray[ACC_X]), float(dataArray[ACC_Y]), float(
                                dataArray[ACC_Z])
                            gyro_x, gyro_y, gyro_z = float(dataArray[GYRO_X]), float(dataArray[GYRO_Y]), float(
                                dataArray[GYRO_Z])
                            lacc_x, lacc_y, lacc_z = float(dataArray[LACC_X]), float(dataArray[LACC_Y]), float(
                                dataArray[LACC_Z])
                            eul_x, eul_y, eul_z = float(dataArray[EUL_X]), float(dataArray[EUL_Y]), float(
                                dataArray[EUL_Z])

                            # Add the raw data to a file
                            with open(RAW_DATA_FILE + ".txt", "a") as raw_data:
                                raw_data.write(f"{timestamp}, {USER}, {acc_x}, {acc_y}, {acc_z}, "
                                               f"{gyro_x}, {gyro_y}, {gyro_z}, "
                                               f"{lacc_x}, {lacc_y}, {lacc_z}, "
                                               f"{eul_x}, {eul_y}, {eul_z}")
                                raw_data.write("\n")

                    if len(sensorData) <= 0:  # All data has been received
                        connection, address = s.accept()
                except KeyboardInterrupt:
                    raise
