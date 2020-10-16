import numpy as np
# from pyquaternion import Quaternion
import time
import math
from math import sqrt, atan2, asin, degrees, radians
import datetime as dt
from pandas import read_csv
import quaternion
import time

raw_data_file = f"data/realtime/raw_data.txt"

steps = 0

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

step_len = 0.65
steps = 0
alpha = 0.9
sample_old = 9.81
threshold = 5.81
steps = 0
def load_csv_file(path, header=None, isWhitespace=False):
    dataframe = read_csv(path, header=header, delim_whitespace=isWhitespace)
    return dataframe.values
raw_data = load_csv_file(path=raw_data_file)
ax = raw_data[:, 2]
ay = raw_data[:, 3]
az = raw_data[:, 4]
gx = raw_data[:, 5]
gy = raw_data[:, 6]
gz = raw_data[:, 7]
ts= raw_data[:,0]
mx= raw_data[:,8]
my= raw_data[:,9]
mz= raw_data[:,10]
acc=raw_data[:, 2:5]


gyro=raw_data[:, 5:8]
mag=raw_data[:,8:11]

# print(gyro)
for i in range(gyro.shape[0]):
    q_gyro = np.quaternion(gyro[i,0], gyro[i,1], gyro[i,2])

q1=q_gyro.components[0]
q2=q_gyro.components[1]
q3=q_gyro.components[2]
q4=q_gyro.components[3]

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
norm_acc = []
for i in range(acc.shape[0]):
 norm = sqrt(acc[i,0] * acc[i,0] + acc[i,1] * acc[i,1] + acc[i,2] * acc[i,2])
 norm_acc.append(norm)


norm = 1 / norm  # use reciprocal for division
ax *= norm
ay *= norm
az *= norm

# Normalise magnetometer measurement
for i in range(mag.shape[0]):
 norm = sqrt(mag[i,0] * mag[i,0] + mag[i,1] * mag[i,1] + mag[i,2] * mag[i,2])
norm = 1 / norm  # use reciprocal for division
mx *= norm
my *= norm
mz *= norm

# Reference direction of Earth's magnetic field
_2q1mx = 2 * q1 * mx
_2q1my = 2 * q1 * my
_2q1mz = 2 * q1 * mz
_2q2mx = 2 * q2 * mx
hx = mx * q1q1 - _2q1my * q4 + _2q1mz * q3 + mx * q2q2 + _2q2 * my * q3 + _2q2 * mz * q4 - mx * q3q3 - mx * q4q4
hy = _2q1mx * q4 + my * q1q1 - _2q1mz * q2 + _2q2mx * q3 - my * q2q2 + my * q3q3 + _2q3 * mz * q4 - my * q4q4

for i in range(hx.shape[0]):
 _2bx = sqrt(hx[i] * hx[i] + hy[i] * hy[i])
_2bz = -_2q1mx * q3 + _2q1my * q2 + mz * q1q1 + _2q2mx * q4 - mz * q2q2 + _2q3 * my * q4 - mz * q3q3 + mz * q4q4
_4bx = 2 * _2bx
_4bz = 2 * _2bz

# Gradient descent algorithm corrective step
s1 = (-_2q3 * (2 * q2q4 - _2q1q3 - ax) + _2q2 * (2 * q1q2 + _2q3q4 - ay) - _2bz * q3 * (_2bx * (0.5 - q3q3 - q4q4)
             + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q4 + _2bz * q2) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
             + _2bx * q3 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

s2 = (_2q4 * (2 * q2q4 - _2q1q3 - ax) + _2q1 * (2 * q1q2 + _2q3q4 - ay) - 4 * q2 * (1 - 2 * q2q2 - 2 * q3q3 - az)
             + _2bz * q4 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q3 + _2bz * q1) * (_2bx * (q2q3 - q1q4)
             + _2bz * (q1q2 + q3q4) - my) + (_2bx * q4 - _4bz * q2) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

s3 = (-_2q1 * (2 * q2q4 - _2q1q3 - ax) + _2q4 * (2 * q1q2 + _2q3q4 - ay) - 4 * q3 * (1 - 2 * q2q2 - 2 * q3q3 - az)
             + (-_4bx * q3 - _2bz * q1) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx)
             + (_2bx * q2 + _2bz * q4) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
             + (_2bx * q1 - _4bz * q3) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

s4 = (_2q2 * (2 * q2q4 - _2q1q3 - ax) + _2q3 * (2 * q1q2 + _2q3q4 - ay) + (-_4bx * q4 + _2bz * q2) * (_2bx * (0.5 - q3q3 - q4q4)
              + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q1 + _2bz * q3) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
              + _2bx * q2 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

for i in range(s1.shape[0]):
 norm = 1 / sqrt(s1[i] * s1[i] + s2[i] * s2[i] + s3[i] * s3[i] + s4[i] * s4[i])    # normalise step magnitude
s1 *= norm
s2 *= norm
s3 *= norm
s4 *= norm

GyroMeasError = radians(40)
beta = sqrt(3.0 / 4.0) * GyroMeasError

# Compute rate of change of quaternion
qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - beta * s1
qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - beta * s2
qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - beta * s3
qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - beta * s4

# Integrate to yield quaternion

q1 += qDot1 * ts
q2 += qDot2 * ts
q3 += qDot3 * ts
q4 += qDot4 * ts
for i in range(q1.shape[0]):
 norm = 1 / sqrt(q1 [i] * q1 [i] + q2 [i] * q2 [i] + q3 [i] * q3[i] + q4[i] * q4[i])    # normalise quaternion

q = q1 * norm, q2 * norm, q3 * norm, q4 * norm
headings = []
for i in range(q1.shape[0]):
 heading = degrees(atan2(2.0 * (q[1][i] * q[2][i] + q[0][i] * q[3][i]),
                         q[0][i] * q[0][i] + q[1][i] * q[1][i] -q[2][i] *q[2][i] -q[3][i] *q[3][i]))
 headings.append(heading)
# print(headings)
from matplotlib import pyplot as plt
fig1 = plt.figure(1)
plt.plot(ts/1000, headings)
plt.ylabel('Heading')
plt.xlabel('Time (s)')

pitchs = []
for i in range(q1.shape[0]):
 pitch = degrees(-asin(2.0 * (q[1][i] * q[3][i] - q[0][i] * q[2][i])))
 pitchs.append(pitch)

fig2 = plt.figure(2)
plt.plot(ts/1000, pitchs)
plt.ylabel('Pitch')
plt.xlabel('Time (s)')

rolls = []
for i in range(q1.shape[0]):
 roll = degrees(atan2(2.0 * (q[0][i] * q[1][i] + q[2][i] * q[3][i]), q[0][i] * q[0][i] - q[1][i] * q[1][i] - q[2][i] * q[2][i] + q[3][i] * q[3][i]))
 rolls.append(roll)

fig3 = plt.figure(3)
plt.plot(ts/1000, rolls)
plt.ylabel('Roll')
plt.xlabel('Time (s)')




#step detetcion
from scipy.signal import find_peaks
peaks, _ = find_peaks(norm_acc, height=0)
steps=peaks
print("Total steps: %d " % len(peaks))

position = np.zeros((len(headings), 2))
positionx, positiony = 0, 0
for i in range(len(headings)):
  positionx += step_len * math.cos(headings[i])
  positiony += step_len * math.sin(headings[i])
  position[i, :] = [positionx, positiony]

print(position)
fig4 = plt.figure(4)
plt.scatter(position[:,0],position[:,1])
plt.ylabel('Y Position (m)')
plt.xlabel('X Position (m)')
plt.show()



# start of new possible step

# for i in range(acc_z.shape[0]):
#  if (acc_z[i] > sample_old) and (acc_z[i] > threshold) and (threshold > sample_old):
#      start_of_step = time.time()
#      # check if we have a step
#  if (acc_z[i] < sample_old) and (acc_z[i] < threshold) and (threshold < sample_old):
#     end_of_step = time.time()
#     step_condition_1 = step_condition_2 = False
#     if end_of_step - start_of_step > 0.1: step_condition_1 = True
#     if (new_max - new_min) > 2: step_condition_2 = True
#     if step_condition_1 and step_condition_2:
#         position[0] += step_len * math.cos(headings[i])
#         position[1] += step_len * math.sin(headings[i])
#         steps += 1
#     new_max = 0
#     new_min = 0
#     sample_old = acc_z[i]
#     # update new_min, new_max for this step
#     if (acc_z[i] < new_min):
#         new_min = acc_z[i]
#     elif (acc_z[i] > new_max):
#         new_max = acc_z[i]
#     # calculate min max for next threshold
#     if (acc_z[i] < min):
#             min = acc_z[i]
#     elif (acc_z[i] > max):
#         max = acc_z[i]
#         i += 1
#         j += 1
#
#         # check if window is reached
#     if (j == j_end):
#         threshold = (max + min) / 2
#         j = 0
#         min = 20
#         max = 0
#
# print(position)
# for i in range(len(headings)):
#  position[0] += step_len * math.cos(headings[i])
#  position[1] += step_len * math.sin(headings[i])
#
#  position.append(position)
# print(position)


# if new_heading [i] < 0: new_heading [i] += 360
#