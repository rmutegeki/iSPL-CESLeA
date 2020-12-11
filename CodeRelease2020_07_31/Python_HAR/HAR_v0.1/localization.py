import numpy as np
# from pyquaternion import Quaternion
import time
import math
from math import sqrt, atan2, asin, degrees, radians
import datetime as dt
from pandas import read_csv
import quaternion
import time
from pandas import read_csv
# from matplotlib import pyplot as plt
from scipy.signal import find_peaks
from findpeaks import findpeaks
steps = []
new_min = 20
min = 20
new_max = 0
max = 0
threshold = 9.81
g = 9.80665
q = [1.0, 0.0, 0.0, 0.0]
pitch = 0
heading = 0
roll = 0
step_len = 0.25
steps = 0
alpha = 0.9
sample_old = 9.81
threshold = 9.81
steps = 0
n_signals = 12  # Number of sensor signal used in ONE sensor (Ex: Acc_xyz, Gyr_xyz, linearAcc_xyz)
sig_start = 0  # The 1st index of sensor signal in the sample (check data formart)
win_size = 10
i = 0
n = 0
raw_data_file = f"data/realtime/raw_data.txt"
LOCATION_RESULT_FILE = 'data/realtime/localization_result.txt'
HEADING = 'data/realtime/localization_result.txt'
acc = np.zeros((len(raw_data_file), 3))
gyro = np.zeros((len(raw_data_file), 3))
mag = np.zeros((len(raw_data_file), 3))
ts = np.zeros((len(raw_data_file), 1))
def line_to_array(_line="1, 2", _delim=",", _dtype=float):
    """ This function converts a line of sensor data to an array"""
    # _arr = _line
    _arr = _line.split(sep=_delim)
    _arr = np.array(_arr, dtype=float)
    # print(_arr)
    return _arr
_data_list = []
_win_data = []
norm_acc = []
d=100
j=100
k=0
ax, ay, az = 0, 0, 0
mx, my, mz = 0, 0, 0
position = np.zeros((len(raw_data_file), 2))
positionx, positiony = 0, 0
start=time.time()
start_of_step=time.time()
try:
    with open(raw_data_file, 'r') as _file:
        while True:
            _line = np.zeros((1, n_signals + 1))
            _line = _file.readline().strip()
            if not _line:
                print("END of the file")
                time.sleep(0.2)
                continue
            _line = line_to_array(_line)
            _data_list.append((_line[sig_start: (sig_start + n_signals)]))
            if len(_data_list) > win_size:
                print("+++++++++++++++++++++++++++++++++++ WINDOW FULL")
                _win_data = np.array(_data_list[0:win_size])
                ts = _win_data[:, 0]
                acc = _win_data[:, 2:5]
                #print(acc)
                gyro = _win_data[:, 5:8]
                mag = _win_data[:, 8:11]
                norm_acceleration = np.zeros((len(acc), 1))
                for i in range(gyro.shape[0]):
                    """ GYROSCOPE"""
                    q_gyro = np.quaternion(gyro[i, 0], gyro[i, 1], gyro[i, 2])
                    q1 = q_gyro.components[0]
                    q2 = q_gyro.components[1]
                    q3 = q_gyro.components[2]
                    q4 = q_gyro.components[3]
                    # Auxiliary variables to avoid repeated arithmetic
                    _2q1 = 2 * q1
                    _2q2 = 2 * q2
                    _2q3 = 2 * q3
                    _2q4 = 2 * q4
                    _2q1q3 = 2 * q1 * q3
                    _2q3q4 = 2 * q3 * q4
                    q1q1 = q1 * q1
                    q1q2 = q1 * q2
                    q1q3 = q1 * q3
                    q1q4 = q1 * q4
                    q2q2 = q2 * q2
                    q2q3 = q2 * q3
                    q2q4 = q2 * q4
                    q3q3 = q3 * q3
                    q3q4 = q3 * q4
                    q4q4 = q4 * q4
                    # Normalise accelerometer measurement
                    norm_acceleration = sqrt(acc[i, 0] * acc[i, 0] + acc[i, 1] * acc[i, 1] + acc[i, 2] * acc[i, 2])
                    norm_acceleration = 1 / norm_acceleration  # use reciprocal for division
                    norm_acc.append(norm_acceleration)
                    #print("----------------------",norm_acceleration)
                    peaks, _ = find_peaks(norm_acc,height=0.11148407402704925)
                    #print(peaks)
                    # fp=findpeaks(method='peakdetect',lookahead=1)
                    # result=fp.fit(norm_acc)
                    #print(result)
                    #print("Total steps: %d " % len(peaks))
                    ax = acc[i, 0] * norm_acceleration
                    ay = acc[i, 1] * norm_acceleration
                    az = acc[i, 2] * norm_acceleration
                    ################################
                    #########################################
                    #norm=sqrt(ax*ax+ay*ay+az*az)
                    # result = fp.fit(norm)
                    #print(norm)
                    # peaks, _ = find_peaks(norm, height=0)
                    # print("Total steps: %d " % len(peaks))
                    """ MAGNETOMETER"""
                    # Normalise magnetometer measurement
                    norm_magnetometer = sqrt(mag[i, 0] * mag[i, 0] + mag[i, 1] * mag[i, 1] + mag[i, 2] * mag[i, 2])
                    norm_magnetometer = 1 / norm_magnetometer  # use reciprocal for division
                    mx = mag[i, 0] * norm_magnetometer
                    my = mag[i, 1] * norm_magnetometer
                    mz = mag[i, 2] * norm_magnetometer
                    # # Reference direction of Earth's magnetic field
                    _2q1mx = 2 * q1 * mx
                    _2q1my = 2 * q1 * my
                    _2q1mz = 2 * q1 * mz
                    _2q2mx = 2 * q2 * mx
                    hx = mx * q1q1 - _2q1my * q4 + _2q1mz * q3 + mx * q2q2 + _2q2 * my * q3 + _2q2 * mz * q4 - mx * q3q3 - mx * q4q4
                    hy = _2q1mx * q4 + my * q1q1 - _2q1mz * q2 + _2q2mx * q3 - my * q2q2 + my * q3q3 + _2q3 * mz * q4 - my * q4q4
                    _2bx = sqrt(hx * hx + hy * hy)
                    _2bz = -_2q1mx * q3 + _2q1my * q2 + mz * q1q1 + _2q2mx * q4 - mz * q2q2 + _2q3 * my * q4 - mz * q3q3 + mz * q4q4
                    _4bx = 2 * _2bx
                    _4bz = 2 * _2bz
                    # Gradient descent algorithm corrective step
                    s1 = (-_2q3 * (2 * q2q4 - _2q1q3 - ax) + _2q2 * (2 * q1q2 + _2q3q4 - ay) - _2bz * q3 * (
                            _2bx * (0.5 - q3q3 - q4q4)
                            + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q4 + _2bz * q2) * (
                                  _2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
                          + _2bx * q3 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

                    s2 = (_2q4 * (2 * q2q4 - _2q1q3 - ax) + _2q1 * (2 * q1q2 + _2q3q4 - ay) - 4 * q2 * (
                            1 - 2 * q2q2 - 2 * q3q3 - az)
                          + _2bz * q4 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (
                                  _2bx * q3 + _2bz * q1) * (_2bx * (q2q3 - q1q4)
                                                            + _2bz * (q1q2 + q3q4) - my) + (
                                  _2bx * q4 - _4bz * q2) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

                    s3 = (-_2q1 * (2 * q2q4 - _2q1q3 - ax) + _2q4 * (2 * q1q2 + _2q3q4 - ay) - 4 * q3 * (
                            1 - 2 * q2q2 - 2 * q3q3 - az)
                          + (-_4bx * q3 - _2bz * q1) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx)
                          + (_2bx * q2 + _2bz * q4) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
                          + (_2bx * q1 - _4bz * q3) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

                    s4 = (_2q2 * (2 * q2q4 - _2q1q3 - ax) + _2q3 * (2 * q1q2 + _2q3q4 - ay) + (
                            -_4bx * q4 + _2bz * q2) * (_2bx * (0.5 - q3q3 - q4q4)
                                                       + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q1 + _2bz * q3) * (
                                  _2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
                          + _2bx * q2 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))
                    norm_step = 1 / sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)  # normalise step magnitude
                    s1 = s1 * norm_step
                    s2 = s2 * norm_step
                    s3 = s3 * norm_step
                    s4 = s4 * norm_step
                    GyroMeasError = radians(40)
                    beta = sqrt(3.0 / 4.0) * GyroMeasError
                    # Compute rate of change of quaternion
                    qDot1 = 0.5 * (-q2 * gyro[i, 0] - q3 * gyro[i, 1] - q4 * gyro[i, 2]) - beta * s1
                    qDot2 = 0.5 * (q1 * gyro[i, 0] + q3 * gyro[i, 2] - q4 * gyro[i, 1]) - beta * s2
                    qDot3 = 0.5 * (q1 * gyro[i, 1] - q2 * gyro[i, 2] + q4 * gyro[i, 0]) - beta * s3
                    qDot4 = 0.5 * (q1 * gyro[i, 2] + q2 * gyro[i, 1] - q3 * gyro[i, 0]) - beta * s4
                    # Integrate to yield quaternion
                    q1 += qDot1 * (ts / 1000)  # millisecond to second conversion
                    q2 += qDot2 * (ts / 1000)
                    q3 += qDot3 * (ts / 1000)
                    q4 += qDot4 * (ts / 1000)
                    norm_quaternion = 1 / sqrt(q1[i] * q1[i] + q2[i] * q2[i] + q3[i] * q3[i] + q4[i] * q4[i])
                    q = q1 * norm_quaternion, q2 * norm_quaternion, q3 * norm_quaternion, q4 * norm_quaternion
                    heading2 = degrees(atan2(2.0 * (q[1][i] * q[2][i] + q[0][i] * q[3][i]),
                                            q[0][i] * q[0][i] + q[1][i] * q[1][i] - q[2][i] * q[2][i] - q[3][i] * q[3][
                                                i]))
                    if gyro[i, 2]<0:gyro[i, 2]=gyro[i, 2]+360
                    heading=165-gyro[i, 2]

                    if heading < 0: heading += 360
                    heading_keep_rad = math.radians(heading)
                    heading_quantized = round(heading / 90) * 90  # -90
                    heading_rad = math.radians(heading_quantized)
                    #print("Heading rad:", heading_rad)
                    #print("............",heading)
                    #start of new possible step
                    # acc[i,2] = (1-alpha) * acc[i,2] + alpha * sample_old
                    # if (acc[i,2]>sample_old) and (acc[i,2]>threshold) and (threshold>sample_old):
                    #     start_of_step =time.time()
                    #     print(",,,,,,,,,,",start_of_step)
                    # #check if we have a step
                    # if(acc[i,2]<sample_old) and (acc[i,2]<threshold) and (threshold<sample_old):
                    #     end_of_step=time.time()
                    #     print("****",end_of_step)
                    #     step_condition_1 = step_condition_2 = False
                    #     if end_of_step - start_of_step > 0.1: step_condition_1 = True
                    #     if (new_max-new_min) > 2: step_condition_2 =True
                    #     if step_condition_1 and step_condition_2:
                    #         positionx += step_len * math.cos(heading)
                    #         positiony += step_len * math.sin(heading)
                    #         position[i, :] = [positionx, positiony]
                    #     new_max = 0
                    #     new_min = 20
                    heading=round(heading, 2)
                    print("Heading:", heading)
                    if (heading !=165.0 ):
                        print(",,,,,")
                    #     positionx[i+1]=positionx[i]
                    #     positiony[i+1]=positiony[i]
                    # else:
                        positionx += step_len * math.cos(heading)
                        positiony += step_len * math.sin(heading)
                        position[i, :] = [positionx, positiony]
                    #position estimation

                    #print(positionx, positiony)
                    # k=k+1
                    # if d==k:
                    #     position=np.mean(position, axis=0)
                    # d=d+j
                    #print(d)
                    #position=math.trunc(position)
                    #print(position)
                    sample_old=acc[i,2]
                    #update new min, new max for this step
                    if(acc[i,2] <new_min):
                        new_min=acc[i,2]
                    elif (acc[i,2]>new_max):
                        new_max = acc[i,2]
                    #calculate min max for next threshold
                    if(acc[i,2]<min):
                        min=acc[i,2]
                    elif(acc[i,2]>max):
                        max=acc[i,2]



                    with open(LOCATION_RESULT_FILE, "a") as position_file:
                        message = f"{round(positionx, 2)},{round(positiony, 2)},{round(heading, 2)},{len(peaks)}"
                        print("*************************************", message)
                        position_file.write(message)
                        position_file.write("\n")
                    del _data_list[0: 12]
            time.sleep(0.01)
except FileNotFoundError as e:
    print("Error at reading file: ", e)
