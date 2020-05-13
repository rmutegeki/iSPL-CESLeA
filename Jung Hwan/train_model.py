# -*- coding: utf-8 -*-
"""


This is for the specimen test by Jung Hwan Kim based on Ronald Source Code!

Version 1.1
Train a CNN+LSTM model to recognize Human activities
Script that defines a CNN_LSTM model, and also employs transfer learning
Built with Keras with a TensorFlow backend
Outputs a model capable of recognizing 3 Human Activities
Created on Mon July 29 09:05:37 2019
@author: Mutegeki Ronald - murogive@gmail.com - iSPL / KNU
"""

# Import support libraries

from JungHwanKim.utils import *  # Contains imports, functions and variables common to all files
from JungHwanKim.cnns import *
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
"""
Global Variables used in this script
"""
# These are the class labels for the target dataset and realtime model (iSPL dataset)
# It is a 3 class classification
ACTIVITIES = {
    0: "WALKING",
    1: "WALKING_UPSTAIRS",
    2: "WALKING_DOWNSTAIRS",
    3: "SITTING",
    4: "STANDING",
    5: "LAYING"

}

SIGNALS = [
           "body_acc_x",
           "body_acc_y",
           "body_acc_z",
           "body_gyro_x",
           "body_gyro_y",
           "body_gyro_z",
           "total_acc_x",
           "total_acc_y",
           "total_acc_z"]


RANDOM_SEED = 7
np.random.seed(42)
tf.set_random_seed(42)

DATASET = "D:/Test_Project/dataset/UCI_HAR_Dataset"


START = datetime.datetime.now()  # Start Time for this script

# Loading the source train and test data
# Functions below are defined in utils.py
# dataset = load_dataset(data_path=f'{DATASET}data.txt', delimiter=",", n_signals=n_signals)
# labels = load_labels(f'{DATASET}labels.txt')

# Shuffle the dataset
# dataset, labels = shuffle(dataset, labels)
# print(dataset.shape, labels.shape)
#
# one_hot_labels = np.asarray(pd.get_dummies(labels.reshape(len(labels))), dtype=np.float32)
# X_train, X_test, y_train, y_test = train_test_split(dataset, one_hot_labels,
#                                                     test_size=0.2, random_state=RANDOM_SEED)


X_train, X_test = load_signals(DATASET, 'train', SIGNALS), load_signals(DATASET, 'test', SIGNALS)
y_train, y_test = load_y(DATASET, 'train'), load_y(DATASET, 'test')

# session_conf = tf.ConfigProto(
#     intra_op_parallelism_threads=2,
#     inter_op_parallelism_threads=2
# )
#
# sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
# K.set_session(sess)

# Configs for the session to run with multiple threads
# session_conf = tf.ConfigProto
session_conf = tf.compat.v1.ConfigProto(
    intra_op_parallelism_threads=2,
    inter_op_parallelism_threads=2
)
# tf.Session(graph=tf.get_default_graph(), config=session_conf)
sess = tf.compat.v1.Session(graph=tf.compat.v1.get_default_graph(), config=session_conf)
tf.compat.v1.keras.backend.get_session(sess)

# Setting Hyperparameters
timesteps = X_train.shape[1]
input_dim = X_train.shape[2]

# ##############################################<Parameters >##########################################################
#print (f"timesteps: {timesteps}, input_dim:{input_dim}")
n_classes = len(ACTIVITIES)
epochs = 50
patience = 25
batch_size = 32
n_hidden = 128
lr = 0.01
momentum = 0.9
clip_value = 0.5



# ###########################################<End of Parameters>#######################################################

print("######### DATASET INFO #########")
print("Timesteps:", timesteps)
print("Input Dim:", input_dim)
print("Training Examples:", len(X_train))
print("Testing Examples:", len(X_test))
print("Testing Epochs:", epochs)
print("Batch Size:", batch_size)

# Reshape data into timeste              ps of sub-sequences to set it up for the Model
n_steps, n_length = 4, 32
n_features = input_dim
#
#
# ############################################<Reshape for LSTM>######################################################
# trainX = X_train.reshape((X_train.shape[0], timesteps, n_features))
# testX = X_test.reshape((X_test.shape[0], timesteps, n_features))
# ###########################################<End of Reshape for LSTM>################################################

###########################################<Reshape for CNN+LSTM>###################################################
trainX = X_train.reshape((X_train.shape[0], n_steps, n_length, n_features))
testX = X_test.reshape((X_test.shape[0], n_steps, n_length, n_features))
########################################<End of Reshape for CNN+LSTM>###############################################

# #########################################<Reshape for CNN2D+LSTM>###################################################
# trainX = X_train.reshape((X_train.shape[0], n_steps, 1, n_length,n_features))
# testX = X_test.reshape(X_test.shape[0], n_steps, 1, n_length, n_features)
# #########################################<End of Reshape for CNN2D+LSTM>############################################

# ###########################################<Reshape for Mixnet>#####################################################
# trainX = X_train.reshape(X_train.shape[0], n_steps * n_features, n_length, 1)
# testX = X_test.reshape(X_test.shape[0],  n_steps * n_features, n_length, 1)
# ############################################<End of Reshape for Mixnet>#############################################
# print (f'trainX.shape:{trainX.shape}')


# We Create a basic model instance to initialize the model that has been built

# model = vanilla_lstm(timesteps, n_features, n_classes)
# model = stacked_lstm(timesteps, n_features, n_classes)
# model = cnn_stacked_lstm(n_length, n_features, n_classes)
model = cnn_lstm(n_length, n_features, n_classes)
# model =  cnn_lstm(n_hidden, n_length, n_features, n_classes)
# model = cnn_stacked_lstm_2d(n_steps, n_length, n_features, n_classes)
# model = cnn_lstm_2d(n_steps, n_length, n_features, n_classes)
# model = call_mixnet(n_steps*n_features,n_length,n_classes)
# model = vanilla_lstm(trainX.shape[1:], n_classes)
opt = adam(learning_rate=lr, clipvalue=clip_value)
model.compile(
    loss='categorical_crossentropy',
    # loss = 'mse',
    optimizer=opt,
    metrics=['accuracy'])
model.summary()

# Import our source model that has been trained on another dataset and adjust it for outputs
# Transfer Learning 101
# source_model_path = "checkpoint/source/model.h5"  # Trained on the UCI HAR Dataset with 6 Activities
# loaded_model = load_model(source_model_path)
# loaded_model.pop()

# new_model = model.set_weights(loaded_model.get_weights())
# print("New model - Transferred but not fine-tuned")
# new_model.summary()
# # Transferred but not fine-tuned
# new_model.save("checkpoint/target/transferred.h5")
checkpoint_path = "checkpoint/target/model_{epoch:02d}_{val_accuracy:.4f}.h5"
checkpoint_dir = os.path.dirname(checkpoint_path)

early_stopping_monitor = EarlyStopping('val_loss', patience=patience)
reduce_lr = ReduceLROnPlateau('val_loss', factor=0.1, patience=int(patience/4),verbose=1)

# The primary use case is to automatically save checkpoints during and at the end of training.
# This way you can use a trained model without having to retrain it, or pick-up training where you left
# of—in case the training process was interrupted.
#
# tf.keras.callbacks.ModelCheckpoint is a callback that performs this task.
# The callback takes a couple of arguments to configure checkpointing.

# Create checkpoint callback
model_checkpoint = ModelCheckpoint(checkpoint_path,
                              monitor='val_loss',
                              save_best_only=True,
                              save_weights_only=True,
                              verbose=1)

callbacks = [model_checkpoint, reduce_lr, early_stopping_monitor]
nb_steps_per_epoch = X_train.shape[0]//batch_size
nb_steps_validation = testX.shape[0]//batch_size
# Training the model
history = model.fit(trainX,
                    y_train,
                    # workers= 1,
                    batch_size=batch_size,
                    # use_multiprocessing= False,
                    validation_data=(testX, y_test),
                    epochs=epochs,
                    shuffle=True,
                    callbacks=callbacks,
                    # steps_per_epoch=nb_steps_per_epoch,
                    # validation_steps= nb_steps_validation
                    )
# pass callback to training
END = datetime.datetime.now()

# Target Model Evaluation
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
