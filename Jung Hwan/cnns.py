from JungHwanKim.utils import *
# from HAR_Jung.mixnets_jung import *
from keras_mixnets import *
# Defining the Model Architecture
# Returns a sequential model


def vanilla_lstm(n_timesteps, n_features, n_classes):
    model = Sequential(name = "Vanilla_LSTM_Model")
    model.add(LSTM(100, input_shape= (n_timesteps, n_features)))
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_classes, activation='softmax'))

    return model

def stacked_lstm(n_timesteps, n_features, n_classes):
    model = Sequential(name = "Stacked_LSTM_Model")


    model.add(LSTM(32,  return_sequences=True, input_shape=(n_timesteps,n_features)))
    model.add(LSTM(32, return_sequences= True))
    model.add(LSTM(32))


    model.add(Dense(100,activation= 'relu' ))
    model.add(Dense(n_classes, activation='softmax'))

    return model

def cnn_stacked_lstm(n_timesteps, n_features, n_classes):
    model = Sequential(name="CNN_Stacked_LSTM_Model")

    model.add(
        TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu'), input_shape=(None, n_timesteps, n_features),
                        name="Convolutional_1"))
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu'), name="Convolutional_2"))
    model.add(TimeDistributed(Dropout(0.2), name="Dropout_1"))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2), name="Maxpool"))
    model.add(TimeDistributed(Flatten(), name="Flatten"))
    model.add(LSTM(256, return_sequences=True))
    model.add(LSTM(256, return_sequences=True))
    model.add(LSTM(256))
    model.add(Dropout(0.2))


    model.add(Dense(128, activation='relu'))


    model.add(Dense(n_classes, activation='softmax'))

    return model

def cnn_lstm(n_length, n_features, n_classes):
    print (f"n_length:{n_length},n_features:{n_features}" )

    m = Sequential(name="CNN+LSTM_Model")
    m.add(
        TimeDistributed(Conv1D
                        (filters=64, kernel_size=3, activation='relu'),
                        input_shape=(None,n_length,n_features),
                        name="Convolutional_1"))

    m.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu'), name="Convolutional_2"))
    m.add(TimeDistributed(Dropout(0.2), name="Dropout_1"))
    m.add(TimeDistributed(MaxPooling1D(pool_size=2), name="Maxpool"))
    m.add(TimeDistributed(Flatten(), name="Flatten"))
    m.add(LSTM(128, name="LSTM"))
    m.add(Dense(100, activation='relu', name="FC_1"))
    m.add(Dropout(0.2, name="Dropout_2")) # previously Ronald set it as 0.2

    # Adding a dense output layer with softmax activation
    m.add(Dense(n_classes, activation='softmax', name="Output"))

    return m


# def cnn_stacked_lstm_2d(n_steps,n_length, n_features, n_classes):
#     model = Sequential()
#     model.add(
#         ConvLSTM2D(filters=64, kernel_size=(1, 3), return_sequences=True, activation='relu', input_shape=(n_steps, 1, n_length, n_features)))
#     model.add(Dropout(0.5))
#     model.add(Flatten())
#     model.add(LSTM(128, return_sequences=True))
#     model.add(LSTM(128, return_sequences=True))
#     model.add(LSTM(128))
#     model.add(Dropout(0.2))
#
#     model.add(Dense(100, activation='relu'))
#
#     model.add(Dense(n_classes, activation='softmax'))
#
#     return model

def cnn_lstm_2d(n_steps,n_length, n_features, n_classes):
    model = Sequential()
    model.add(ConvLSTM2D(filters=64, kernel_size= (1,3), activation='relu', input_shape=(n_steps, 1, n_length, n_features)))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_classes, activation='softmax'))

    return model


def call_mixnet(row,col,n_classes):
    model = MixNetSmall((row,col,1), include_top=True, classes=n_classes)
    # model = MixNetMedium((row,col,1), include_top=True, classes=n_classes)
    # model = MixNetLarge((row,col,1), include_top=True, classes = n_classes)
    # I will add more for testing

    return model

# def rnn_lstm(n_hidden, n_classes, n_length, n_features):
#     m = Sequential(name = "RNN+LSTM_Model")
#     m.add(TimeDistributed(LSTM(n_hidden, return_sequences=True, input_shape=(None, n_length, n_features))))
#     m.add(Dropout(0.2))
#
#     m.add(LSTM(n_hidden))