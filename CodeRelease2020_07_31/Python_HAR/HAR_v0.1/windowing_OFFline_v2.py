"""
****************************** WINDOWING - SMARTPHONE ******************************
- v2:
    + work with multiple data files
    + combine all the experiment data
    + remove all the data of IDLE activity

- OFFLINE used only
- For sensor data collected from smartphone
- Split data into fixed length windows with overlap
- Raw data format: [label, received time, transmitted time, device_id, Acc_xyz, Gyr_xyz, Mag_xyz, LinearAcc_xyz]
- Window data format: each line is data of 1 window reshape from [win_size, n_signals]

"""
import numpy as np
from pandas import read_csv
import time


n_signals = 12  # Number of sensor signal used in ONE sensor (Ex: Acc_xyz, Gyr_xyz, linearAcc_xyz)
sig_start = 4   # The 1st index of sensor signal in the sample (check raw data formart)

freq = 50  # Sampling rate (unit: samples/second)
win_time = 2.56  # Time duration of a window (unit: second)
win_size = int(freq * win_time)  # Size of a window (unit: data samples)
overlap = int(win_size * 0.5)

dataset_version = "TEST_Thu_overlap50"
data_path = "data/offline/"
list_experiments = [
    "Alwin-left_pocket/raw_data_2020-08-27_22_8_28_sensor1"
    # , "Alwin-left_pocket/raw_data_2020-08-27_22_34_11_sensor1"
    # , "Savina/raw_data_2020-09-01_21_1_0_sensor1"
    # , "Thu/raw_data_2020-09-01_17_32_29_sensor1_handfree"
    # , "Thu/raw_data_2020-09-01_17_49_21_sensor1-right_pocket"
    ]

# # Keep the window data of each experiment separately
# raw_data_file = f"data/offline/raw_data_{experiment_name}.txt"

# To combine the data of all experiments into 1 file
win_data_file = f"data/offline/win_data_{dataset_version}.txt"
win_label_file = f"data/offline/win_label_{dataset_version}.txt"


def load_csv_file(path, header=None, isWhitespace=False):
    dataframe = read_csv(path, header=header, delim_whitespace=isWhitespace)
    return dataframe.values


def windowing(_data_path, _list_experiments, _win_data_file, _win_label_file,
              _win_size, _overlap):
    """ Windowing - Split the data into fix-length windows with overlap """
    for _exp in _list_experiments:
        _raw_data_file = f"{_data_path}{_exp}.txt"

        _raw_data = load_csv_file(path=_raw_data_file)
        print(_raw_data.shape)

        y = _raw_data[:, 0].astype(int)
        X = _raw_data[:, sig_start:(sig_start+n_signals)]
        print(X.shape)

        win_idx = 0
        i = 0
        while i <= X.shape[0] - _win_size:
            _win_data = X[i:i + _win_size, :]
            _win_data_line = np.reshape(_win_data, (1, -1))  # reshape win_data to 1 row vector for saving into txt file
            # win_label = max(y[i: i+_win_size], key=y[i: i+_win_size].count)   # Choose the most frequent label in that window
            _win_label = np.argmax(np.bincount(y[i: i + _win_size]))  # Choose the most frequent label in that window
            print("i = ", i, ", label = ", _win_label, ", win_idx = ", win_idx)

            if _win_label < 1:
                # Not save the window data of IDLE activity
                i = i + 1
                print("SKIP the IDLE data")
                continue

            # Save to win_data_file
            with open(_win_data_file, "a") as _data_file,\
                    open(_win_label_file, "a") as _label_file:
                np.savetxt(_data_file, _win_data_line, fmt="%s", delimiter=',')
                # np.savetxt(_label_file, win_label, fmt="%s", delimiter=',')
                _label_file.write(str(_win_label))
                _label_file.write("\n")

            win_idx = win_idx + 1
            i = i + _win_size - _overlap


"""********************************************* EXECUTION PART *********************************************"""
if __name__ == "__main__":

    windowing(data_path, list_experiments, win_data_file, win_label_file,
              win_size, overlap)

