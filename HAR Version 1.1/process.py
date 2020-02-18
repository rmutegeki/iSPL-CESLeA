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


all_files = []
all_file_threads = []
OFFLINE = True

# List all Settings/Configs from the WITHROBOT Sensor
ID = 0
TIMESTEP = 1
MILLIS = 2
ACC_X, ACC_Y, ACC_Z = 3, 4, 5
GYRO_X, GYRO_Y, GYRO_Z = 6, 7, 8
LACC_X, LACC_Y, LACC_Z, = 9, 10, 11
MAG_X, MAG_Y, MAG_Z = 12, 13, 14
EUL_X, EUL_Y, EUL_Z = 15, 16, 17

# The name of the file storing our data for this session
# Offline data
if OFFLINE:
    dt = datetime.datetime.now()
    RAW_DATA_FILE = f"data/processed/raw_data_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}_sensor"
else:
    # Online data
    RAW_DATA_FILE = "data/user"


# Let's continuously follow updates to this file
def follow(thefile):
    thefile.seek(0, 0)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


# process the data for this file
def process_data(file_name_):
    count = 1
    while True:
        try:
            src = f'data/raw/{file_name_}'
            dest = f'data/processed/{file_name_}'
            file_location = open(src, "r")
            file_reader = follow(file_location)
            for line in file_reader:  # read the lines of data coming in to the raw data file
                if not line == "":
                    timestamp, data_samples = line.split('>')
                    for sample in data_samples.split(';'):
                        # Remove the start and end flags
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
                                if count >= 100:
                                    print(f"{timestamp}: {sample}")
                                    count = 1
                                count += 1
                                sensor_id = int(sample[ID])
                                timestep = int(sample[TIMESTEP])
                                millis = int(sample[MILLIS])
                                acc_x, acc_y, acc_z = float(sample[ACC_X]), float(sample[ACC_Y]), float(
                                    sample[ACC_Z])
                                gyro_x, gyro_y, gyro_z = float(sample[GYRO_X]), float(sample[GYRO_Y]), float(
                                    sample[GYRO_Z])
                                lacc_x, lacc_y, lacc_z = float(sample[LACC_X]), float(sample[LACC_Y]), float(
                                    sample[LACC_Z])
                                mag_x, mag_y, mag_z = float(sample[MAG_X]), float(sample[MAG_Y]), float(
                                    sample[MAG_Z])
                                eul_x, eul_y, eul_z = float(sample[EUL_X]), float(sample[EUL_Y]), float(
                                    sample[EUL_Z])
                                # Add the raw data to a file
                                with open(f"{dest}", "a") as raw_data:
                                    raw_data.write(f"{timestamp},{sensor_id},{timestep},{millis},"
                                                   f"{acc_x},{acc_y},{acc_z},"
                                                   f"{gyro_x},{gyro_y},{gyro_z},"
                                                   f"{lacc_x},{lacc_y},{lacc_z},"
                                                   f"{mag_x},{mag_y},{mag_z},"
                                                   f"{eul_x},{eul_y},{eul_z}")
                                    raw_data.write("\n")
                            except:
                                print(f"Ill formed data:{sys.exc_info()[0]}")
                                continue
        except (FileNotFoundError, IOError, KeyboardInterrupt) as e:
            print("Error processing file: ", e)
            continue


# Thread 1 handles new file additions
def find_new_files():
    for f in all_files:
        f.close()

    del all_files[:]

    while True:
        try:
            # check in the raw data folder to find any new files
            # get a list of files in raw data
            for rootDir, subdirs, filenames in os.walk('data/raw/'):
                for filename in filenames:
                    # Skip file entry with the same name
                    if filename in all_files:
                        pass
                    else:
                        print("Fs: ", filename)
                        all_files.append(filename)
                        thread = Thread(target=process_data, args=(filename,))
                        thread.daemon = True
                        thread.start()
                        all_file_threads.append(thread)
            time.sleep(1)

        except:
            print("Error Following files")


if __name__ == "__main__":
    find_new_files()
    for t in all_file_threads:
        t.join()
