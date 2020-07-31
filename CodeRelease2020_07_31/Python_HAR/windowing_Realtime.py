"""
****************************** WINDOWING - SMARTPHONE ******************************

- OFFLINE used only
- For sensor data collected from smartphone
- Split data into fixed length windows with overlap
- Raw data format: [time, device_id, Acc_xyz, Gyr_xyz, LinearAcc_xyz]
- Window data format: each line is data of 1 window reshape from [win_size, n_signals]

"""
import numpy as np
from pandas import read_csv
import time

n_signals = 9   # Number of sensor signal used in ONE sensor (Ex: Acc_xyz, Gyr_xyz, linearAcc_xyz)
sig_start = 2   # The 1st index of sensor signal in the sample (check data formart)

freq = 50  # Sampling rate (unit: samples/second)
win_time = 2.56  # Time duration of a window (unit: second)
win_size = int(freq * win_time)  # Size of a window (unit: data samples)
overlap = int(win_size * 0.5)


raw_data_file = f"data/realtime/raw_data.txt"
win_data_file = f"data/realtime/win_data.txt"


def line_to_array(_line="1, 2", _delim=",", _dtype=float):
    """ This function converts a line of sensor data to an array"""
    # _arr = _line
    _arr = _line.split(sep=_delim)
    _arr = np.array(_arr)
    # print(_arr)
    return _arr


def windowing_realtime(raw_data_file, win_data_file,
              win_size, overlap):
    """ Windowing - Split the data into fix-length windows with overlap """
    _data_list = []
    try:
        with open(raw_data_file, 'r') as _file:
            while True:
                _line = np.zeros((1, n_signals + 1))
                _line = _file.readline().strip()
                if not _line:
                    print("END of the file")
                    continue
                _line = line_to_array(_line)

                _data_list.append((_line[sig_start:]))

                # Enough window data:
                if len(_data_list) > win_size:
                    print("+++++++++++++++++++++++++++++++++++ WINDOW FULL")
                    _win_data = np.array(_data_list[0:win_size])
                    _win_data_line = np.reshape(_win_data, (1, np.prod(_win_data.shape)))

                    # Save to win_data_file
                    with open(win_data_file, "a") as _win_data_file:
                        np.savetxt(_win_data_file, _win_data_line, fmt="%s", delimiter=',')

                    # Remove the non-overlap part of the window in the _data_list
                    del _data_list[0: (win_size - overlap)]
                time.sleep(0.01)

    except FileNotFoundError as e:
        print("Error at reading file: ", e)

"""********************************************* EXECUTION PART *********************************************"""
if __name__ == "__main__":
    windowing_realtime(raw_data_file, win_data_file,
              win_size, overlap)

