
# -*- coding: utf-8 -*-
"""
Make predictions on the trained model in realtime
Script that defines a CNN_LSTM model, and also employs transfer learning
Built with Keras with a TensorFlow backend
Outputs a model capable of recognizing 3 Human Activities
Created on Mon July 29 09:05:37 2019
@author: Mutegeki Ronald - murogive@gmail.com - iSPL / KNU
"""

# Import support libraries
from utils import *  # Contains imports, functions and variables common to all files

# Activities are the class labels
# It is a 3 class classification
ACTIVITIES = {
    0: "STANDING",
    1: "SITTING",
    2: "WALKING",
}

# Setting up keras information
# Configuring a session
session_conf = tf.ConfigProto(
    intra_op_parallelism_threads=2,
    inter_op_parallelism_threads=2
)
sess = tf.compat.v1.Session(graph=tf.compat.v1.get_default_graph(), config=session_conf)
K.set_session(sess)
# Trained model location
checkpoint = "checkpoint/target/model2.h5"
# checkpoint = "checkpoint/cnn_lstm/model.ckpt"
model = load_model(checkpoint)
"""
# Do the same thing we did during training
"""
# reshape data into time steps of sub-sequences
n_steps, n_length = 4, 32
n_features = 6
# Setting up
activity_data_log_file = {1: "data/activity_data1_log.txt", 2: "data/activity_data2_log.txt"}
activity_data = {1: "data/activity1.txt", 2: "data/activity2.txt"}
raw_prediction_data_file = {1: "data/predict/user1.txt", 2: "data/predict/user2.txt"}


# Predict user's activity
def predict(user=1, n_signals=6):
    while True:
        try:
            file_location = open(raw_prediction_data_file[user], "r")
            file_reader = follow(file_location)
            for line in file_reader:  # read the lines of data coming in to the user's data file
                # Reshape our data to (m, number of signals, timesteps)
                data_array = np.array(line.split(",")).reshape((1, n_signals, -1))
                data_array = np.transpose(data_array, (0, 2, 1))
                print(f'User: {user} Data Shape: {data_array.shape}')
                inputs = data_array.reshape((data_array.shape[0], n_steps, n_length, n_features))
                scores = model.predict(inputs)[0]
                print("Prediction Scores:", scores)

                predicted_label = max(range(len(scores)), key=lambda x: scores[x])
                predicted_label = ACTIVITIES[predicted_label]
                print("Predicted Label: ", predicted_label)

                # Add the predicted label to file
                with open(activity_data[user], "w") as file:
                    file.write(f'{predicted_label}')
                with open(activity_data_log_file[user], "a") as file:
                    file.write(f"{scores}, {predicted_label}")
                    file.write("\n")
        except (FileNotFoundError, IOError, KeyboardInterrupt) as e:
            print("Error :", e)
            time.sleep(2)


if __name__ == "__main__":
    predict(1)
