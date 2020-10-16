"""
************************************* PREDICTION MODEL *************************************
- Load the pretrain model from checkpoint file
- Read the data from window_data.txt
- Predict the activity
- Save the result to prediction_result.txt
"""

# Make predictions on the trained model
import numpy as np
import tensorflow as tf
from keras.models import load_model
import datetime
import time

n_sensors = 1
n_signals = 12               # Number of sensor signal used in 1 sensor (Ex: Acc_xyz, Gyr_xyz, linearAcc_xyz)
freq = 50                   # Sampling rate (unit: samples/second or Hz)
win_time = 2.56                # Time duration of a window (unit: second)
win_size = int(freq * win_time)  # Size of a window (unit: data samples)
overlap = int(win_size * 0.5)


data_shape = (win_size, n_signals)
targetModel_shape = (1, win_size, n_signals)    # the 1st dimension is the number of sample: online -> = 1
basedModel_shape = (1, win_size, n_signals)  # shape of the data in the pre-trained model
# transpose_shape = [0, 1, 3, 2]     # using np.transpose to transpose from original_shape to desired_shape

# for 4-D input data
n_frames = 4
desired_shape = (1, n_frames, int(win_size/n_frames), n_signals)    # input shape of the pre-train model


# files' path
WIN_DATA_FILE = 'data/realtime/win_data.txt'
RESULT_FILE = 'data/realtime/prediction_result.txt'
LOG_FILE = 'data/realtime/log_data.txt'    # save the prediction result with probability for each class

# List of activities
ACTIVITIES = ["WALKING", "STANDING", "SITTING", "LYING", "RUNNING", "IDLE"]


# Load the pre-trained model
# input_shape of the pre-trained mode: [64, 9]
MODEL_NAME = "model_stacked_LSTM"     # Ex: model_LSTM, model_stacked_LSTM, model_CNN1D_LSTM_v1 (model zoo from utils)
checkpoint = f"pretrained_models/ckp_{MODEL_NAME}"

model = load_model(checkpoint)
model.summary()


# Predict user's activity
def predict():
    try:
        with open(WIN_DATA_FILE, "r") as _win_data_file:
            while True:
                _line = _win_data_file.readline().strip()
                if not _line:
                    print("There is no new window data here -> WAIT")
                    time.sleep(0.5)
                    continue

                _input_data = np.array(_line.split(",")).reshape(targetModel_shape)
                print("INPUT DATA SHAPE: ", _input_data.shape)

                _scores = model.predict(_input_data)[0]
                print(_scores)
                _result = ACTIVITIES[_scores.argmax(0)]
                print('++++++++++++++++ Predicted activity: ', _result)

                # Add the predicted label to file
                with open(RESULT_FILE, "a") as file:
                    file.write(f'{_result}')
                    file.write("\n")
                with open(LOG_FILE, "a") as file:
                    file.write(f"{_scores}, {_result}")
                    file.write("\n")
    except (FileNotFoundError, IOError, KeyboardInterrupt) as e:
        print("Error :", e)
        time.sleep(2)


if __name__ == "__main__":
    # predict()
    while True:
        predict()

