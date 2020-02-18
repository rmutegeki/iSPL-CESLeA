import datetime
import sys
import time
import socket
from queue import Queue
from threading import Thread
import numpy as np
# Deleting files we no longer need
import os
import fnmatch
import sys

NUMBER_OF_THREADS = 4
# 1. handles client connections
# 2. reads data from sensors and adds it to a queue. Also, processes the data and stores it to file
JOB_NUMBER = [1, 2]
job_queue = Queue()
# A queue to which we add data from the sensors and is processed by other threads
data_queue = Queue()
all_connections = []
all_address = []
OFFLINE = False

# List all Settings/Configs from the WITHROBOT Sensor
ID = 0
ACC_X, ACC_Y, ACC_Z = 1, 2, 3
GYRO_X, GYRO_Y, GYRO_Z = 4, 5, 6
LACC_X, LACC_Y, LACC_Z, = 7, 8, 9
EUL_X, EUL_Y, EUL_Z = 10, 11, 12


position_data_file = {1: "data/position_data1.txt", 2: "data/position_data2.txt", 3: "data/position_data3.txt"}
position_data = {1: "data/position1.txt", 2: "data/position2.txt", 3: "data/position3.txt"}

# The name of the file storing our data for this session
# Offline data
if OFFLINE:
    dt = datetime.datetime.now()
    RAW_DATA_FILE = f"data/raw_data_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}_sensor"
else:
    # Online data
    RAW_DATA_FILE = "data/user"


# Thread 1 handles socket connections and disconnections
# Create a Socket (connect two devices)
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 5500
        s = socket.socket()
        print('Socket created')

    except socket.error as msg:
        print("Socket creation error: " + str(msg))


# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.bind((host, port))
        s.listen(10)
        print('Socket now listening')

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()


# Handling connection from multiple clients and saving to a list
# Closing previous connections when server.py is restarted
def accepting_connections():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = s.accept()
            # Remove client entry with the same ip address
            idx = 0
            for ip, pt in all_address:
                if address[0] == ip:
                    print("Client already exists")
                    all_connections[idx].close()
                    del all_connections[idx]
                    del all_address[idx]
                idx += 1

            s.setblocking(True)  # prevents a timeout

            all_connections.append(conn)
            all_address.append(address)

            print(f"Connection has been established : {address[0]}")
            print(f"All clients:", all_address)

            t = Thread(target=receive_data, args=(conn,))
            t.daemon = True
            t.start()

        except:
            print("Error accepting connections")


# Combines different pieces of data from the sensor and adds them together while checking whether this is the end flag
def combine_pieces(current_batch, new_data):
    if new_data[-1] is ';':
        return f'{current_batch}{new_data}', True
    else:
        return f'{current_batch}{new_data}', False


# 3rd thread functions - 1) Receive data from sensors 2) Add received data to data queue
def receive_data(conn):
    current_batch = ''
    while True:
        try:
            # receive data from sensor
            buffer = conn.recv(10240)
            if len(buffer) > 0:
                # let's read the buffer into memory
                new_data = buffer.decode("ascii")
                current_batch, end = combine_pieces(current_batch, new_data)
                if end:
                    timestamp = f"{time.time():.3f}"
                    data_samples = list(current_batch.split(";"))
                    data_samples.insert(0, timestamp)

                    # add data samples to data queue
                    data_queue.put(data_samples)
                    current_batch = ""
                # All data has been received
                continue
        except:
            print("Error receiving data")
            conn.close()
            break
        else:
            print("All data has been received from the client")
            conn.close()
            break


# OFFLINE
# 2nd thread functions - 1) Read data from the queue. 2) Process it
def process_data_offline():
    count = 1
    while True:
        # List unpacking
        timestamp, *data = data_queue.get()
        if count >= 20:
            print(f"{timestamp}: {data}")
            count = 1
        for sample in data:
            count += 1
            sample = sample.replace("s", "").replace("e", "")
            sample = sample.split(",")

            if len(sample) < EUL_Z:
                # Let's only print something when there is data but is just not enough
                if len(sample) > 3:
                    print(sample)
                    print("Not enough data")
                continue
            else:
                try:
                    sensor_id = int(sample[ID])
                    acc_x, acc_y, acc_z = float(sample[ACC_X]), float(sample[ACC_Y]), float(
                        sample[ACC_Z])
                    gyro_x, gyro_y, gyro_z = float(sample[GYRO_X]), float(sample[GYRO_Y]), float(
                        sample[GYRO_Z])
                    lacc_x, lacc_y, lacc_z = float(sample[LACC_X]), float(sample[LACC_Y]), float(
                        sample[LACC_Z])
                    eul_x, eul_y, eul_z = float(sample[EUL_X]), float(sample[EUL_Y]), float(
                        sample[EUL_Z])
                    # Add the raw data to a file
                    with open(f"{RAW_DATA_FILE}{sensor_id}.txt", "a") as raw_data:
                        raw_data.write(f"{timestamp}, {sensor_id}, {acc_x}, {acc_y}, {acc_z}, "
                                       f"{gyro_x}, {gyro_y}, {gyro_z}, "
                                       f"{lacc_x}, {lacc_y}, {lacc_z}, "
                                       f"{eul_x}, {eul_y}, {eul_z}")
                        raw_data.write("\n")
                except :
                    print(f"Ill formed data:{sys.exc_info()[0]}")
                    continue


# def clear_data(dir_):
#     # Get a list of all files in directory
#     for rootDir, subdirs, filenames in os.walk(dir_):
#         # Find the files that matches the given pattern
#         for filename in fnmatch.filter(filenames, '*.txt'):
#             try:
#                 os.remove(os.path.join(rootDir, filename))
#             except OSError:
#                 print("Error while deleting file")


# ONLINE
# 2nd thread functions - 1) Read data from the queue. 2) Process it and save it to file
# Realtime and online
def process_data_online():
    # Clear all data files
    # os.remove("data")
    # count_for_user = {1: 0, 2: 0}
    round1 = {1: True, 2: True, 3: True}
    acc_x_list = {1: [], }
    acc_y_list = {1: [], }
    acc_z_list = {1: [], }
    gyro_x_list = {1: [], }
    gyro_y_list = {1: [], }
    gyro_z_list = {1: [], }
    lacc_x_list = {1: [], }
    lacc_y_list = {1: [], }
    lacc_z_list = {1: [], }
    win_size = 128
    win_end = {1: win_size, }

    # Localization support variables
    leg_length = {1: 0.65, }
    offset = {1: 1.0, }
    first_step = {1: True, }
    no_samples = {1: 0, }
    pos_x, pos_y, acc_magnitude, pos_mag = {1: 0.0, }, {1: 0.0, }, {1: 0.0, }, {1: 0.0, }

    while True:
        # List unpacking
        timestamp, *data = data_queue.get()

        for sample in data:
            sample = sample.replace("s", "").replace("e", "")
            sample = sample.split(",")
            # print(sample)

            if len(sample) < EUL_Z:
                # Let's only print something when there is data but is just not enough
                if len(sample) > 3:
                    print(sample)
                    print("Not enough data")
                continue
            try:
                sensor_id = int(sample[ID])
                acc_x, acc_y, acc_z = float(sample[ACC_X]), float(sample[ACC_Y]), float(
                    sample[ACC_Z])
                gyro_x, gyro_y, gyro_z = float(sample[GYRO_X]), float(sample[GYRO_Y]), float(
                    sample[GYRO_Z])
                lacc_x, lacc_y, lacc_z = float(sample[LACC_X]), float(sample[LACC_Y]), float(
                    sample[LACC_Z])
                eul_x, eul_y, eul_z = float(sample[EUL_X]), float(sample[EUL_Y]), float(
                    sample[EUL_Z])

                # Let's log the data to a file
                # Add the raw data to a file
                with open(f"{RAW_DATA_FILE}{sensor_id}_log.txt", "a") as raw_data:
                    raw_data.write(f"{timestamp}, {sensor_id}, {acc_x}, {acc_y}, {acc_z}, "
                                   f"{gyro_x}, {gyro_y}, {gyro_z}, "
                                   f"{lacc_x}, {lacc_y}, {lacc_z}, "
                                   f"{eul_x}, {eul_y}, {eul_z}")
                    raw_data.write("\n")

                # For each sensor
                # Let's do localization
                acc_magnitude[sensor_id] = np.sqrt(acc_x ** 2 + acc_y ** 2 + acc_z ** 2) - 9.81

                if acc_magnitude[sensor_id] > 0.9 and np.abs(eul_z) < 100:
                    # print("Let's get our position!")
                    if first_step[sensor_id]:
                        offset[sensor_id] = eul_x
                        first_step[sensor_id] = False
                    pos_x[sensor_id] += 2 * (2 * leg_length[sensor_id]*np.cos((eul_y-10) * np.pi/180)) * np.cos((eul_x-offset[sensor_id]) * np.pi / 180)
                    pos_y[sensor_id] += 2 * (2 * leg_length[sensor_id]*np.cos((eul_y-10) * np.pi/180)) * np.sin((eul_x-offset[sensor_id]) * np.pi / 180)
                    pos_mag[sensor_id] += 2 * (2 * leg_length[sensor_id]*np.cos((eul_y-10) * np.pi/180))
                    position = f'{pos_x[sensor_id]},{pos_y[sensor_id]}'
                    try:
                        with open(position_data_file[sensor_id], "a") as position_data_:
                            print(f'Position >> x:{pos_x[sensor_id]}, y:{pos_y[sensor_id]}')
                            position_data_.write(position)
                            position_data_.write("\n")
                    except IOError as e:
                        print("Caught an error: ", e)
                    try:
                        with open(position_data[sensor_id], "w") as PositionFile:
                            pos = "%.2f, %.2f" % (pos_x[sensor_id], pos_y[sensor_id])
                            PositionFile.write(pos)
                    except IOError as e:
                        print("Caught an error: ", e)
                no_samples[sensor_id] += 1

                # Add this sensor's accelerometer and gyroscope values to their respective lists
                acc_x_list[sensor_id].append(acc_x)
                acc_y_list[sensor_id].append(acc_y)
                acc_z_list[sensor_id].append(acc_z)
                gyro_x_list[sensor_id].append(gyro_x)
                gyro_y_list[sensor_id].append(gyro_y)
                gyro_z_list[sensor_id].append(gyro_z)
                lacc_x_list[sensor_id].append(lacc_x)  # Future
                lacc_y_list[sensor_id].append(lacc_y)
                lacc_z_list[sensor_id].append(lacc_z)

                if round1[sensor_id] and len(acc_x_list[sensor_id]) == win_size \
                        or len(acc_x_list[sensor_id]) == (win_end[sensor_id] + (win_size / 2)):

                    # We've gotten enough data for this window
                    print(f"At least 128 values of data for user {sensor_id}. Data Count: {len(acc_x_list[sensor_id])}")
                    win_end[sensor_id] = len(acc_x_list[sensor_id])

                    # We are only interested in the current 128 items in the list

                    # Let's add it to a file
                    data_file = f"data/predict/user{sensor_id}.txt"
                    data_string = f'{",".join(map(str, acc_x_list[sensor_id][-win_size:]))},' \
                                  f'{",".join(map(str, acc_y_list[sensor_id][-win_size:]))},' \
                                  f'{",".join(map(str, acc_z_list[sensor_id][-win_size:]))},' \
                                  f'{",".join(map(str, gyro_x_list[sensor_id][-win_size:]))},' \
                                  f'{",".join(map(str, gyro_y_list[sensor_id][-win_size:]))},' \
                                  f'{",".join(map(str, gyro_z_list[sensor_id][-win_size:]))},' \
                                  f'{",".join(map(str, lacc_x_list[sensor_id][-win_size:]))},' \
                                  f'{",".join(map(str, lacc_y_list[sensor_id][-win_size:]))},' \
                                  f'{",".join(map(str, lacc_z_list[sensor_id][-win_size:]))}'
                    try:
                        with open(data_file, 'a') as thefile:
                            thefile.write(data_string)
                            thefile.write("\n")
                    except IOError as e:
                        print("Caught an error trying to save to a file: ", e)
                        continue

                    round1[sensor_id] += 1
            except:
                print(f"Ill formed data:{sys.exc_info()[0]}")
                continue


# Create worker threads
def create_workers():
    # Threads that maintain connections and obtain data
    for _ in range(NUMBER_OF_THREADS):
        t = Thread(target=work)
        t.daemon = True
        t.start()


# Do next job that is in the queue (handle connections, receive data)
def work():
    while True:
        x = job_queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            if OFFLINE:
                process_data_offline()
            else:
                process_data_online()

        job_queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        job_queue.put(x)

    job_queue.join()


def main():
    # create connections and collect data
    create_workers()
    create_jobs()

    # ALl data has been processed
    data_queue.join()


if __name__ == "__main__":
    main()
