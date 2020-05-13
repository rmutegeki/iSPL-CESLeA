# -*- coding: utf-8 -*-
"""
Train a CNN+LSTM model to recognize Human activities
Created on Mon July 29 09:05:37 2019
@author: Mutegeki Ronald - murogive@gmail.com - iSPL / KNU
"""

# Import support libraries
from JungHwanKim.utils import *  # Contains imports, functions and variables common to all files


"""
Global Variables used in this script
"""
# These are the class labels for the UCI HAR dataset
# It is a 6 class classification
ACTIVITIES = {
    0: 'WALKING',
    1: 'WALKING_UPSTAIRS',
    2: 'WALKING_DOWNSTAIRS',
    3: 'SITTING',
    4: 'STANDING',
    5: 'LAYING',
}

START = datetime.datetime.now()

RANDOM_SEED = 7
np.random.seed(42)
tf.random.set_seed(42)
# Data directory
DATADIR = 'dataset/UCI_HAR_Dataset'

# Raw IMU data signals from Accelerometer and Gyroscope in x,y,z directions
# Signals are filtered to have only body acceleration excluding the acceleration due to gravity
SIGNALS = [
    "body_acc_x",
    "body_acc_y",
    "body_acc_z",
    "body_gyro_x",
    "body_gyro_y",
    "body_gyro_z",
    "total_acc_x",
    "total_acc_y",
    "total_acc_z",
]

# Loading the target dataset
# Functions below are defined in utils.py
X_train, X_test = load_signals(DATADIR, 'train', SIGNALS), load_signals(DATADIR, 'test', SIGNALS)
y_train, y_test = load_y(DATADIR, 'train'), load_y(DATADIR, 'test')

# Configs for the session to run with multiple threads
session_conf = tf.compat.v1.ConfigProto(
    intra_op_parallelism_threads=2,
    inter_op_parallelism_threads=2
)

sess =  tf.compat.v1.Session(graph=tf.compat.v1.get_default_graph(), config=session_conf)
tf.compat.v1.keras.backend.get_session(sess)

# Setting Hyperparameters
timesteps = X_train.shape[1]
input_dim = X_train.shape[2]
n_classes = len(ACTIVITIES)
epochs = 20
batch_size = 64
n_hidden = 128
lr = 0.025

print("######### SOURCEDATASET INFO #########")
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
        TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu'), input_shape=(None, n_length, n_features), name="Convolutional_1"))
    m.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu'), name="Convolutional_2"))
    m.add(TimeDistributed(Dropout(0.2), name="Dropout_1"))
    m.add(TimeDistributed(MaxPooling1D(pool_size=2), name="Maxpool"))
    m.add(TimeDistributed(Flatten(), name="Flatten"))
    m.add(LSTM(n_hidden, name="LSTM"))
    m.add(Dense(100, activation='relu', name="FC_1"))
    m.add(Dropout(0.2, name="Dropout_2"))

    # Adding a dense output layer with softmax activation
    m.add(Dense(n_classes, activation='softmax', name="Output"))

    m.compile(loss='categorical_crossentropy',
              optimizer="adam",
              metrics=['accuracy'])

    return m


# Create a basic model instance
model = create_model()
model.summary()

base_model_path = "../iSPL-CESLeA/HAR_Jung/checkpoint/source/model.h5"
# model.load_weights(base_model_path)  # For loading a pretrained model
early_stopping_monitor = EarlyStopping(patience=5)

checkpoint_path = "../iSPL-CESLeA/HAR_Jung/checkpoint/source/model.h5"
checkpoint_dir = os.path.dirname(checkpoint_path)

# Create checkpoint callback
cp_callback = ModelCheckpoint(checkpoint_path,
                              monitor='val_loss',
                              save_best_only=True,
                              save_weights_only=False,
                              verbose=1)
# Training the model
history = model.fit(trainX,
                    y_train,
                    batch_size=batch_size,
                    validation_data=(testX, y_test),
                    epochs=epochs,
                    callbacks=[cp_callback])  # pass callback to training

END = datetime.datetime.now()

# Source Model Evaluation
if __name__ == "__main__":
    # Confusion Matrix from Utils
    cm = confusion_m(y_test, model.predict(testX), ACTIVITIES)
    print(f"Confusion Matrix\n{cm}")

    loss, acc = model.evaluate(testX, y_test)
    print("Source model, accuracy: {:5.2f}%".format(100 * acc))
    print("Source model, Loss: {:5.2f}%".format(100 * loss))

    predictions = model.predict(testX).argmax(1)
    testY = y_test.argmax(1)

    print("")
    print("Precision: {}%".format(100 * metrics.precision_score(testY, predictions, average="weighted")))
    print("Recall: {}%".format(100 * metrics.recall_score(testY, predictions, average="weighted")))
    print("f1_score: {}%".format(100 * metrics.f1_score(testY, predictions, average="weighted")))

    print("")
    print("Confusion Matrix:")
    confusion_matrix = metrics.confusion_matrix(testY, predictions)
    print(confusion_matrix)
    normalised_confusion_matrix = np.array(confusion_matrix, dtype=np.float32) / np.sum(confusion_matrix) * 100

    print("")
    print("Confusion matrix (normalised to % of total test data):")
    print(normalised_confusion_matrix)

    # Plot Results:
    width = 12
    height = 12
    plt.figure(figsize=(width, height))
    plt.imshow(
        normalised_confusion_matrix,
        interpolation='nearest',
        cmap=plt.cm.rainbow
    )
    plt.title("Source Task \nConfusion matrix \n(normalised to % of total test data)")
    plt.colorbar()
    tick_marks = np.arange(n_classes)
    plt.xticks(tick_marks, ACTIVITIES)
    plt.yticks(tick_marks, ACTIVITIES)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()
    plt.pause(2)

    plot_graphs(history, 'loss')
    plot_graphs(history, 'accuracy')

    # Time Spent
    print("Start:", START)
    print("End:", END)
    print("Time Spent(s): ", END - START)
