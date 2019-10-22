# Importing Libraries
import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Importing tensorflow
np.random.seed(42)
import tensorflow as tf

tf.set_random_seed(42)

# Import Keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import LSTM, TimeDistributed, Conv1D, MaxPooling1D, Flatten
from keras.layers.core import Dense, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint

# These are the class labels for the target dataset
# It is also a 6 class classification
ACTIVITIES = {
    0: 'WALKING',
    1: 'WALKING_UPSTAIRS',
    2: 'WALKING_DOWNSTAIRS',
    3: 'SITTING',
    4: 'STANDING',
    5: 'LAYING',
}

START = datetime.datetime.now()


# Utility function to print the confusion matrix
def confusion_matrix_(Y_true, Y_pred):
    Y_true = pd.Series([ACTIVITIES[y] for y in np.argmax(Y_true, axis=1)])
    Y_pred = pd.Series([ACTIVITIES[y] for y in np.argmax(Y_pred, axis=1)])

    return pd.crosstab(Y_true, Y_pred, rownames=['True'], colnames=['Pred'])


# Data directory
DATADIR = 'dataset/UCI_HAR_Dataset'

# Raw data signals
# Signals are from Accelerometer and Gyroscope
# The signals are in x,y,z directions
# Sensor signals are filtered to have only body acceleration
# excluding the acceleration due to gravity
# Triaxial acceleration from the accelerometer is total acceleration
SIGNALS = [
    # "body_acc_x",
    # "body_acc_y",
    # "body_acc_z",
    "body_gyro_x",
    "body_gyro_y",
    "body_gyro_z",
    "total_acc_x",
    "total_acc_y",
    "total_acc_z"
]


# Utility function to read the data from csv file
def _read_csv(filename):
    return pd.read_csv(filename, delim_whitespace=True, header=None)


# Utility function to load the load
def load_signals(subset):
    signals_data = []

    for signal in SIGNALS:
        filename = f'{DATADIR}/{subset}/Inertial Signals/{signal}_{subset}.txt'
        signals_data.append(
            _read_csv(filename).as_matrix()
        )

    # Transpose is used to change the dimensionality of the output,
    # aggregating the signals by combination of sample/timestep.
    # Resultant shape is (7352 train/2947 test samples, 128 timesteps, 6 signals)
    return np.transpose(signals_data, (1, 2, 0))


def load_y(subset):
    """
    The objective that we are trying to predict is a integer, from 1 to 6,
    that represents a human activity. We return a binary representation of
    every sample objective as a 6 bits vector using One Hot Encoding
    (https://pandas.pydata.org/pandas-docs/stable/generated/pandas.get_dummies.html)
    """
    filename = f'{DATADIR}/{subset}/y_{subset}.txt'
    y = _read_csv(filename)[0]

    return pd.get_dummies(y).as_matrix()


def load_data():
    """
    Obtain the dataset from multiple files.
    Returns: X_train, X_test, y_train, y_test
    """
    X_train, X_test = load_signals('train'), load_signals('test')
    y_train, y_test = load_y('train'), load_y('test')

    return X_train, X_test, y_train, y_test


# Configuring a session
session_conf = tf.ConfigProto(
    intra_op_parallelism_threads=2,
    inter_op_parallelism_threads=2
)

sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
K.set_session(sess)


# Utility function to count the number of classes
def _count_classes(y):
    return len(set([tuple(category) for category in y]))


# Loading the train and test source data
X_train, X_test, Y_train, Y_test = load_data()
timesteps = X_train[0].shape[1]
input_dim = X_train.shape[2]
n_classes = _count_classes(Y_train)

# Model
# Initializing parameters
epochs = 15
batch_size = 64
n_hidden = 128
lr = 0.025

print("Source Dataset Info:")
print("Timesteps:", timesteps)
print("Input Dim:", input_dim)
print("Training Examples:", len(X_train))
print("Testing Examples:", len(X_test))
print("Testing Epochs:", epochs)
print("Batch Size:", batch_size)

# reshape data into time steps of sub-sequences
n_steps, n_length = 4, 32
n_features = input_dim
trainX = X_train.reshape((X_train.shape[0], n_steps, n_length, n_features))
testX = X_test.reshape((X_test.shape[0], n_steps, n_length, n_features))


# Defining the Model Architecture
# Returns a short sequential model
def create_model():
    # define model
    # define model
    m = Sequential()
    m.add(
        TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu'), input_shape=(None, n_length, n_features)))
    m.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu')))
    m.add(TimeDistributed(Dropout(0.2)))
    m.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    m.add(TimeDistributed(Flatten()))
    m.add(LSTM(n_hidden))
    m.add(Dense(100, activation='relu'))
    m.add(Dropout(0.2))
    # Adding a dense output layer with softmax activation
    m.add(Dense(n_classes, activation='softmax'))

    m.compile(loss='categorical_crossentropy',
              optimizer="adam",
              metrics=['accuracy'])

    return m


# Method for Plotting graphs
def plot_graphs(history, string):
    plt.plot(history.history[string])
    plt.plot(history.history['val_' + string])
    plt.xlabel("Epochs")
    plt.ylabel(string)
    plt.legend([string, 'val_' + string])
    plt.show()


# Create a basic model instance
model = create_model()

base_model_path = "checkpoint/source/model.h5"
# model.load_weights(base_model_path)

model.summary()

early_stopping_monitor = EarlyStopping(patience=3)

# The primary use case is to automatically save checkpoints during and at the end of training.
# This way you can use a trained model without having to retrain it, or pick-up training where you left
# of—in case the training process was interrupted.
#
# tf.keras.callbacks.ModelCheckpoint is a callback that performs this task.
# The callback takes a couple of arguments to configure checkpointing.
checkpoint_path = "checkpoint/source/model.h5"
checkpoint_dir = os.path.dirname(checkpoint_path)

# Create checkpoint callback
cp_callback = ModelCheckpoint(checkpoint_path,
                              monitor='val_loss',
                              save_best_only=True,
                              save_weights_only=False,
                              verbose=1)
# Training the model
history = model.fit(trainX,
                    Y_train,
                    batch_size=batch_size,
                    validation_data=(testX, Y_test),
                    epochs=epochs,
                    callbacks=[cp_callback])  # pass callback to training

END = datetime.datetime.now()

# Source Model Evaluation
# Confusion Matrix
# model.load_weights(checkpoint_path)
cm = confusion_matrix_(Y_test, model.predict(testX))
print(cm)

loss, acc = model.evaluate(testX, Y_test)
print("Source model, accuracy: {:5.2f}%".format(100 * acc))

score = model.evaluate(testX, Y_test)
print(score)

plot_graphs(history, 'loss')
plot_graphs(history, 'accuracy')

# Time Spent
print("Start:", START)
print("End:", END)
print("Time Spent(s): ", END - START)
