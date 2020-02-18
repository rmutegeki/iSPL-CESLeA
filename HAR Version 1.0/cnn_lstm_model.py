# -*- coding: utf-8 -*-
"""
Train a CNN+LSTM model to recognize Human activities
Created on Mon July 29 09:05:37 2019
@author: Mutegeki Ronald - murogive@gmail.com - iSPL / KNU
"""

from utils import *


"""
Global Variables used in this script
"""
# These are the class labels for the target dataset and realtime model (iSPL dataset)
# It is a 3 class classification
ACTIVITIES = {
    0: "STANDING",
    1: "SITTING",
    2: "WALKING",
}

# Used variables
RANDOM_SEED = 7
np.random.seed(42)
tf.set_random_seed(42)
DATASET = "dataset/iSPL/"

START = datetime.datetime.now()  # Start Time for this script

# Loading the train and test target data from the dataset
# Functions defined in utils.py
dataset = load_dataset(f'{DATASET}data.txt', ",", 6)
labels = load_labels(f'{DATASET}labels.txt')

one_hot_labels = np.asarray(pd.get_dummies(labels.reshape(len(labels))), dtype=np.float32)
X_train, X_test, y_train, y_test = train_test_split(dataset, one_hot_labels,
                                                    test_size=0.2, random_state=RANDOM_SEED)

# Configs for the session
session_conf = tf.ConfigProto(
    intra_op_parallelism_threads=2,
    inter_op_parallelism_threads=2
)

sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
K.set_session(sess)

timesteps = X_train[0].shape[1]
input_dim = X_train.shape[2]
n_classes = len(ACTIVITIES)  # Number of classes (6)

# Model
# Initializing parameters
epochs = 20
batch_size = 32
n_hidden = 128

print("Dataset Info:")
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
model.summary()

# Bring in our source model
source_model_path = "checkpoint/source/model.h5"
loaded_model = load_model(source_model_path)
loaded_model.pop()
loaded_model.pop()
new_model = model.set_weights(loaded_model.get_weights())
print("New model")
new_model.summary()
new_model.save('transferred.h5')

early_stopping_monitor = EarlyStopping(patience=3)

# The primary use case is to automatically save checkpoints during and at the end of training.
# This way you can use a trained model without having to retrain it, or pick-up training where you left
# of—in case the training process was interrupted.
#
# tf.keras.callbacks.ModelCheckpoint is a callback that performs this task.
# The callback takes a couple of arguments to configure checkpointing.
checkpoint_path = "checkpoint/target/model.h5"
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
                    validation_split=0.2,
                    # validation_data=(testX, y_test),
                    epochs=epochs,
                    shuffle=True,
                    callbacks=[cp_callback])  # pass callback to training

END = datetime.datetime.now()

# Source Model Evaluation
# Confusion Matrix from common
cm = confusion_m(y_test, model.predict(testX))
print(cm)

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
