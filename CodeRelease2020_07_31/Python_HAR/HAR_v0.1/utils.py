import numpy as np
import pandas as pd
from pandas import read_csv, read_excel
from numpy import dstack
from keras.utils import to_categorical, plot_model
from keras.models import Sequential
from keras.layers import LSTM, GRU, Dense
from keras.layers import Conv1D, MaxPooling1D, SeparableConv1D
from keras.layers import TimeDistributed, Flatten, Reshape, Dropout
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix



"""
#****************************************** MODEL ZOO ******************************************#
"""
def model_LSTM(_inputshape, _n_classes, _n_hiddens=128):
    """ Require 3D data: [n_samples, n_timesteps (or sequence size), n_features]"""
    _model = Sequential()
    _model.add(LSTM(_n_hiddens, input_shape=_inputshape))
    # _model.add(Dropout(0.3))
    _model.add(Dense(100, activation='relu'))
    _model.add(Dense(_n_classes, activation='softmax'))

    _model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return _model


def model_stacked_LSTM(_inputshape, _n_classes, _n_hiddens=128):
    """ Require 3D data: [n_samples, n_timesteps (or sequence size), n_features]"""
    _model = Sequential()
    _model.add(LSTM(_n_hiddens, input_shape=_inputshape, return_sequences=True))
    _model.add(LSTM(_n_hiddens))
    # _model.add(Dropout(0.3))
    _model.add(Dense(100, activation='relu'))
    _model.add(Dense(_n_classes, activation='softmax'))

    _model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    plot_model(_model, show_shapes=True, to_file='model_LSTM.png')
    return _model


def model_CNN1D_LSTM_v1(input_shape=(1, 2, 3), n_classes=5, n_hiddens=64):
    """ CNN1D_LSTM version 1: Divide 1 window into several smaller frames, then apply CNN to each frame
    - Input data format: [None, n_frames, n_timesteps, n_signals]"""
    model = Sequential()

    model.add(TimeDistributed(Conv1D(filters=32, kernel_size=3, activation='relu', padding='same', data_format="channels_last"),
                              input_shape=input_shape))
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=5, activation='relu')))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=5, activation='relu')))
    model.add(TimeDistributed(Conv1D(filters=32, kernel_size=3, activation='relu')))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(n_hiddens))
    model.add(Dropout(0.5))
    model.add(Dense(n_hiddens, activation='relu'))
    model.add(Dense(n_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

"""
#************************************ RESULTS VISUALIZATION functions ************************************#
"""
# plot train and test process
def plot_process(_history, _title):
    # accuracy
    fig1 = plt.figure(1)
    plt.plot(_history.history['accuracy'], label='train')
    plt.plot(_history.history['val_accuracy'], label='test')
    plt.title(_title)
    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')

    # loss
    fig2 = plt.figure(2)
    plt.plot(_history.history['loss'], label='Training Loss')
    plt.plot(_history.history['val_loss'], label='Test Loss')
    plt.title(_title)
    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.show()


# summarize scores
def summarize_results(_scores):
    print(_scores)
    m, s = np.mean(_scores), np.std(_scores)
    print('Accuracy: %.3f%% (+/-%.3f)' % (m, s))


"""
#************************************ SMALL functions for loading DATASETS ************************************#
"""
# 1 - load a single file as numpy array (csv file)
def load_file(filepath, header=None, isWhitespace=False):
    dataframe = read_csv(filepath, header=header, delim_whitespace=isWhitespace)
    return dataframe.values


# 2 - load win data and reshape to the original shape
# X: [n_wins, win_size, n_signals]
# y: one-hot encoder
def load_dataset(win_data_file, win_label_file, win_size=128, n_signals=9):
    X = load_file(win_data_file)
    y = load_file(win_label_file)
    X = np.reshape(X, (-1, win_size, n_signals))
    y = to_categorical(y)
    print("load_dataset: ", X.shape, y.shape)

    return X, y


"""
#************************************ ACTIVITES ************************************#
"""
ACTIVITIES = ["WALKING", "STANDING", "SITTING", "LYING", "RUNNING", "IDLE"]