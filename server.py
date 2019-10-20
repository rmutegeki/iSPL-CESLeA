import datetime
import socket
import threading
from queue import Queue

NUMBER_OF_THREADS = 3
# 1. handles client connections
# 2. reads data from sensors and adds it to a queue. Also, processes the data and stores it to file
JOB_NUMBER = [1, 2, 3]
job_queue = Queue()
# A queue to which we add data from the sensors and is processed by other threads
data_queue = Queue()
all_connections = []
all_address = []
sensors = [1, 2]

# List all Settings/Configs from the WITHROBOT Sensor
ID = 0
ACC_X, ACC_Y, ACC_Z = 1, 2, 3
GYRO_X, GYRO_Y, GYRO_Z = 4, 5, 6
LACC_X, LACC_Y, LACC_Z, = 7, 8, 9
EUL_X, EUL_Y, EUL_Z = 10, 11, 12

dt = datetime.datetime.now()
# The name of the file storing our data for this session
RAW_DATA_FILE = f"data/raw_data_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}"


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

        except:
            print("Error accepting connections")


# 2nd thread functions - 1) Receive data from sensors 2) Add received data to data queue
def receive_data():
    while True:
        for i, conn in enumerate(all_connections):
            try:
                # receive data from sensor
                buffer = conn.recv(10240)
                if len(buffer) > 0:
                    # let's read the buffer into memory
                    current_batch = buffer.decode("ascii")
                    data_samples = list(current_batch.split(";"))
                    timestamp = str(datetime.datetime.now())
                    data_samples.insert(0, timestamp)

                    # add data samples to data queue
                    data_queue.put(data_samples)
                    # All data has been received
            except:
                print("Error receiving data")
                del all_connections[i]
                del all_address[i]
                continue


# 3rd thread functions - 1) Read data from the queue. 2) Process it
def get_data(conn):
    try:
        # receive data from sensor
        buffer = conn.recv(10240)
        if len(buffer) > 0:
            # let's read the buffer into memory
            current_batch = buffer.decode("ascii")
            data_samples = list(current_batch.split(";"))
            timestamp = str(datetime.datetime.now())
            data_samples.insert(0, timestamp)

            # add data samples to data queue
            data_queue.put(data_samples)
            # All data has been received
            return True
        else:
            return False
    except:
        print("Error receiving data")
        return False


# 3rd thread functions - 1) Read data from the queue. 2) Process it
def store_data():
    count = 1
    while True:
        # List unpacking
        try:
            timestamp, *data = data_queue.get()
            if count >= 50:
                print(f"{timestamp}: {data}")
                count = 1
            for sample in data:
                count += 1
                sample = sample.replace("s", "").replace("e", "")
                sample = sample.split(",")

                if len(sample) < EUL_Z:
                    continue
                else:
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
                    with open(f"{RAW_DATA_FILE}_sensor{sensor_id}.txt", "a") as raw_data:
                        raw_data.write(f"{timestamp}, {sensor_id}, {acc_x}, {acc_y}, {acc_z}, "
                                       f"{gyro_x}, {gyro_y}, {gyro_z}, "
                                       f"{lacc_x}, {lacc_y}, {lacc_z}, "
                                       f"{eul_x}, {eul_y}, {eul_z}")
                        raw_data.write("\n")
        except:
            print("Ill formed data:")
            continue


# Create worker threads
def create_workers():
    # Threads that maintain connections and obtain data
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
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
            receive_data()
        if x == 3:
            store_data()

        job_queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        job_queue.put(x)

    job_queue.join()


if __name__ == "__main__":
    for sensor in sensors:
        with open(f"{RAW_DATA_FILE}_sensor{sensor}.txt", "w") as file:
            file.write("timestamp, sensor, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, "
                       "lacc_x, lacc_y, lacc_z, eul_x, eul_y, eul_z")
            file.write("\n")

    # create connections and collect data
    create_workers()
    create_jobs()

    # ALl data has been processed
    data_queue.join()
