import os
import numpy as np
import tensorflow as tf
from keras.utils import plot_model
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

import utils

n_signals = 12
win_size = 128

experiment_name = "TEST_Thu_overlap70"
win_data_file = f"data/offline/win_data_{experiment_name}.txt"
win_label_file = f"data/offline/win_label_{experiment_name}.txt"

# Load data: X has the form of [n_wins, win_size, n_signals]
X, y = utils.load_dataset(win_data_file, win_label_file, win_size, n_signals)

""" ************************************* HYPER-PARAMETERS *************************************"""
MODEL_NAME = "model_CNN1D_LSTM_v1"     # Ex: model_LSTM, model_stacked_LSTM, model_CNN1D_LSTM_v1 (model zoo from utils)
n_hiddens = 128     # for LSTM layers
n_frames = 4        # for Timedistributed layer-based models (win_size should be divided by n_frames with no remainder)
verbose, epochs, batch_size = 2, 100, 128


"""******************************** CHECKPOINT ********************************"""
# The callback takes a couple of arguments to configure checkpointing.
checkpoint_path = f"pretrained_models/Thu_3act/ckp_{MODEL_NAME}"
bool_save_ckp = True

# Create checkpoint callback
cp_callback = ModelCheckpoint(filepath=checkpoint_path,
                              monitor='val_loss',
                              save_best_only=False,
                              save_weights_only=False,
                              verbose=1)
rlrop = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=10)


def evaluate_model(_model, _X_train, _y_train, _X_test, _y_test):
    _model.summary()
    plot_model(_model, show_shapes=True, to_file=f"pretrained_models/{MODEL_NAME}.png")
    _model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    _history = _model.fit(_X_train, _y_train,
                        validation_data=(_X_test, _y_test),
                        callbacks=[cp_callback, rlrop],                # pass callback to training
                        epochs=epochs, batch_size=batch_size, verbose=verbose) if bool_save_ckp \
        else _model.fit(_X_train, _y_train,
                        validation_data=(_X_test, _y_test),
                        callbacks=[rlrop],                              # pass callback to training
                        epochs=epochs, batch_size=batch_size, verbose=verbose)

    # evaluate model
    _, _accuracy = _model.evaluate(_X_test, _y_test, batch_size=batch_size, verbose=verbose)
    _y_predict = _model.predict(_X_test).argmax(1)
    # _y_predict = 0

    return _accuracy, _history, _y_predict


"""*************************************** EXECUTION ***************************************"""
repeats = 1
scores = list()
for r in range(repeats):

    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)
    X_train = X_test = X
    y_train = y_test = y
    y_cm = np.argmax(y_test, 1)     # reverse y from categorical to original label for confusion matrix plot
    print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

    if MODEL_NAME == "model_LSTM":
        """desired shape: [n_wins, win_size, n_signals]"""
        my_model = utils.model_LSTM(_inputshape=X_train.shape[1:], _n_classes=y_train.shape[1], _n_hiddens=n_hiddens)

    elif MODEL_NAME == "model_stacked_LSTM":
        """desired shape: [n_wins, win_size, n_signals]"""
        my_model = utils.model_stacked_LSTM(_inputshape=X_train.shape[1:], _n_classes=y_train.shape[1], _n_hiddens=n_hiddens)

    elif MODEL_NAME == "model_CNN1D_LSTM_v1":
        """ desired shape: [n_wins, n_frames, n_timesteps, n_signals]"""
        X_train = np.reshape(X_train, (X_train.shape[0], n_frames, -1, n_signals))
        X_test = np.reshape(X_test, (X_test.shape[0], n_frames, -1, n_signals))
        my_model = utils.model_CNN1D_LSTM_v1(input_shape=X_train.shape[1:], n_classes=y_train.shape[1], n_hiddens=n_hiddens)

    score, history, y_predict = evaluate_model(my_model, X_train, y_train, X_test, y_test)

    score = score * 100.0
    print('>#%d: %.3f' % (r + 1, score))
    scores.append(score)
    utils.summarize_results(scores)

    utils.plot_process(history, MODEL_NAME)

    # utils.plot_CM(y_cm, y_predict, class_names, "LSTM model - Stretch sensors")



