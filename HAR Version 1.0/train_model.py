# To store data
import datetime
import pickle
# To measure time
from time import time

# To create nicer plots
import seaborn as sns
import tensorflow as tf
# To build models
from sklearn.model_selection import train_test_split

# Utility functions
from utils import *

# To do linear algebra
# To create plots
# To investigate distributions

ACTIVITIES = {
    "1": "STANDING",
    "2": "SITTING",
    "3": "WALKING",
}

# Some utility variables
RANDOM_SEED = 7
np.random.seed(RANDOM_SEED)  # Setting random seed for uniformity
NORMALIZED = False  # Should we normalize the dataset?
AUGMENTED = False  # Should we augment dataset?
FEATURES = False  # Should we do feature extraction?
FEATURE_SET = "stft"  # We use STFT features. Available: stft and dwt
DATASET = "dataset/iSPL/"


def create_2_lstm_model(inputs):
    """
    Model adopted from https://www.curiousily.com/posts/human-activity-recognition-using-lstms-on-android/
    It has 2 fully connected and 2 hidden layers each with 64 units
    :param inputs:
    :return:
    """
    W = {
        'hidden': tf.Variable(tf.random_normal([nx, nh])),
        'output': tf.Variable(tf.random_normal([nh, ny]))
    }
    biases = {
        'hidden': tf.Variable(tf.random.normal([nh], mean=1.0)),
        'output': tf.Variable(tf.random.normal([ny]))
    }

    X = tf.transpose(inputs, [1, 0, 2])
    X = tf.reshape(X, [-1, nx])
    hidden = tf.compat.v1.nn.relu(tf.matmul(X, W['hidden']) + biases['hidden'])
    hidden = tf.split(hidden, n_time_steps, 0)

    # Stack 2 LSTM layers
    cells = [tf.compat.v1.nn.rnn_cell.BasicLSTMCell(nh, forget_bias=1.0) for _ in range(2)]
    # tf.keras.layers.LSTMCell
    lstm_layers = tf.compat.v1.nn.rnn_cell.MultiRNNCell(cells)
    # tf.keras.layers.StackedRNNCells

    outputs, _ = tf.compat.v1.nn.static_rnn(lstm_layers, hidden, dtype=tf.float32)
    # keras.layers.RNN(cell, unroll=True)

    # Get output for the last time step
    lstm_last_output = outputs[-1]

    return tf.matmul(lstm_last_output, W['output']) + biases['output']


if __name__ == "__main__":
    dataset = load_dataset(f'{DATASET}data.txt', ",", 6)
    labels = load_labels(f'{DATASET}labels.txt')

    # We use the original dataset and labels that are onehot encoded
    one_hot_labels = np.asarray(pd.get_dummies(labels.reshape(len(labels))), dtype=np.float32)
    X_train, X_test, y_train, y_test = train_test_split(dataset, one_hot_labels,
                                                        test_size=0.2, random_state=RANDOM_SEED)

    n_time_steps = X_train.shape[1]  # 128 timesteps
    ny = len(ACTIVITIES)  # Number of classes (6)
    nx = X_train.shape[2]  # Number of features (9, acc, gyr, lin_acc)
    nh = 64  # Number of hidden units

    # Create placeholders for our model
    tf.compat.v1.reset_default_graph()

    # We name this tensor so as to use it during realtime predictions
    X = tf.compat.v1.placeholder(tf.float32, [None, n_time_steps, nx], name="input")
    Y = tf.compat.v1.placeholder(tf.float32, [None, ny])

    pred_Y = create_2_lstm_model(X)

    pred_softmax = tf.compat.v1.nn.softmax(pred_Y, name="yhat")

    # Training Hyperparameters
    # We use L2 regularization
    L2_LOSS = 0.0015
    learning_rate = 0.0025
    epochs = 20
    batch_size = 32

    l2 = L2_LOSS * sum(tf.compat.v1.nn.l2_loss(tf_var) for tf_var in tf.compat.v1.trainable_variables())

    loss = tf.reduce_mean(tf.compat.v1.nn.softmax_cross_entropy_with_logits_v2(logits=pred_Y, labels=Y)) + l2
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss)

    correct_pred = tf.equal(tf.argmax(pred_softmax, 1), tf.argmax(Y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_pred, dtype=tf.float32))

    # Training
    saver = tf.train.Saver()

    history = dict(train_loss=[],
                   train_acc=[],
                   test_loss=[],
                   test_acc=[])
    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())

    train_count = len(X_train)

    # Loop for training
    print("Started training:", datetime.datetime.now())
    for i in range(1, epochs + 1):
        for start, end in zip(range(0, train_count, batch_size),
                              range(batch_size, train_count + 1, batch_size)):
            sess.run(optimizer, feed_dict={X: X_train[start:end],
                                           Y: y_train[start:end]})

        _, acc_train, loss_train = sess.run([pred_softmax, accuracy, loss], feed_dict={
            X: X_train, Y: y_train})

        _, acc_test, loss_test = sess.run([pred_softmax, accuracy, loss], feed_dict={
            X: X_test, Y: y_test})

        history['train_loss'].append(loss_train)
        history['train_acc'].append(acc_train)
        history['test_loss'].append(loss_test)
        history['test_acc'].append(acc_test)

        if i != 1 and i % 5 != 0:
            continue

        print(
            f'epoch: {i} \t| Train acc: {acc_train} loss:{loss_train} \t| Test accuracy: {acc_test} loss: {loss_test}')

    # Make predictions on test data
    tic = time()
    predictions, acc_final, loss_final = sess.run([pred_softmax, accuracy, loss], feed_dict={X: X_test, Y: y_test})
    # Finished Predicting
    toc = time()
    print("Predicting:", (toc - tic) * 1000, "ms")

    print()
    print(f'final results: accuracy: {acc_final} loss: {loss_final}')

    # Storing to disk
    pickle.dump(predictions, open("training/predictions.p", "wb"))
    pickle.dump(history, open("training/history.p", "wb"))
    tf.io.write_graph(sess.graph_def, '/checkpoint/model_2l', 'har.pbtxt')
    saver.save(sess, save_path="checkpoint/model_2l/har.ckpt")
    sess.close()

    # Loading the model back
    history = pickle.load(open("training/history.p", "rb"))
    predictions = pickle.load(open("training/predictions.p", "rb"))

    # Evaluation
    plt.figure(figsize=(12, 8))

    plt.plot(np.array(history['train_loss']), "r--", label="Train loss")
    plt.plot(np.array(history['train_acc']), "g--", label="Train accuracy")

    plt.plot(np.array(history['test_loss']), "r-", label="Test loss")
    plt.plot(np.array(history['test_acc']), "g-", label="Test accuracy")

    plt.title("Training session's progress over iterations")
    plt.legend(loc='upper right', shadow=True)
    plt.ylabel('Training Progress (Loss or Accuracy values)')
    plt.xlabel('Training Epoch')
    plt.ylim(0)

    plt.show()

    LABELS = [item for _, item in ACTIVITIES.items()]

    max_test = np.argmax(y_test, axis=1)
    max_predictions = np.argmax(predictions, axis=1)
    cm = confusion_matrix(max_test, max_predictions)

    plt.figure(figsize=(16, 14))
    sns.heatmap(cm, xticklabels=LABELS, yticklabels=LABELS, annot=True, fmt="d")
    plt.title("Confusion matrix")
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()

    # Plot non-normalized confusion matrix
    cm, _ = plot_confusion_matrix(max_test, max_predictions, classes=LABELS,
                                  title='LSTM Confusion matrix, without normalization')

    # Plot normalized confusion matrix
    cm_normalized, _ = plot_confusion_matrix(max_test, max_predictions, classes=LABELS, normalize=True,
                                             title='LSTM Confusion matrix, Normalized')

    np.set_printoptions(precision=2)
    plt.show()
