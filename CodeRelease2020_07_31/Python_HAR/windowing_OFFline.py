"""
****************************** WINDOWING - SMARTPHONE ******************************

- OFFLINE used only
- For sensor data collected from smartphone
- Split data into fixed length windows with overlap
- Raw data format: [label, time, device_id, Acc_xyz, Gyr_xyz, LinearAcc_xyz]
- Window data format: each line is data of 1 window reshape from [win_size, n_signals]

"""
import numpy as np
from pandas import read_csv
import time

n_signals = 12  # Number of sensor signal used in ONE sensor (Ex: Acc_xyz, Gyr_xyz, linearAcc_xyz)
sig_start = 3   # The 1st index of sensor signal in the sample (check data formart)

freq = 50  # Sampling rate (unit: samples/second)
win_time = 2.56  # Time duration of a window (unit: second)
win_size = int(freq * win_time)  # Size of a window (unit: data samples)
overlap = int(win_size * 0.5)

experiment_name = "2020-07-31_8-23-46_device1"
raw_data_file = f"data/offline/raw_data_{experiment_name}.txt"
win_data_file = f"data/offline/win_data_{experiment_name}.txt"
win_label_file = f"data/offline/win_label_{experiment_name}.txt"


def load_csv_file(path, header=None, isWhitespace=False):
    dataframe = read_csv(path, header=header, delim_whitespace=isWhitespace)
    return dataframe.values


def windowing(raw_data_file, win_data_file, win_label_file,
              win_size, overlap):
    """ Windowing - Split the data into fix-length windows with overlap """
    raw_data = load_csv_file(path=raw_data_file)
    y = raw_data[:, 0]
    y = y.astype(int)
    X = raw_data[:, 3:]
    print(X.shape)
    print(raw_data.shape)
    win_idx = 0
    i = 0
    while i <= X.shape[0] - win_size:
        win_data = X[i:i+win_size, :]
        win_data_line = np.reshape(win_data, (1, -1))  # reshape win_data to 1 row vector for saving into txt file
        # win_label = max(y[i: i+win_size], key=y[i: i+win_size].count)   # Choose the most frequent label in that window
        win_label = np.argmax(np.bincount(y[i: i+win_size]))  # Choose the most frequent label in that window
        print("i = ", i, ", label = ", win_label, ", win_idx = ", win_idx)

        # Save to win_data_file
        with open(win_data_file, "a") as _data_file,\
            open (win_label_file, "a") as _label_file:
            np.savetxt(_data_file, win_data_line, fmt="%s", delimiter=',')
            # np.savetxt(_label_file, win_label, fmt="%s", delimiter=',')
            _label_file.write(str(win_label))
            _label_file.write("\n")


        win_idx = win_idx + 1
        i = i + win_size - overlap


"""********************************************* EXECUTION PART *********************************************"""
if __name__ == "__main__":
    windowing(raw_data_file, win_data_file, win_label_file,
              win_size, overlap)

