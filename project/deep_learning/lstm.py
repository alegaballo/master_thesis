from keras.models import Sequential
from keras.layers import Dense, Recurrent, BatchNormalization, LSTM
from keras.regularizers import l2
from keras.callbacks import Callback
from pandas import DataFrame
import numpy as np
import pickle
import matplotlib.pyplot as plt
import time
import os
from sklearn.model_selection import train_test_split


MODEL_DIR = './../trained_models/lstm/'
STAT_FILE = 'arch_cmp.txt'

def print_samples(x, y, n=10):
    higher = len(x)
    print(higher)
    for i in range(n):
        j = np.random.randint(0, higher)
        print(x[j], y[j])

class TestCallback(Callback):
    def __init__(self, test_data):
        self.test_data = test_data[:2]
        self.net_params = test_data[2:]
        self.epochs = [16, 32, 64, 128]

    def on_epoch_end(self, epoch, logs={}):
        if epoch in self.epochs:
            x, y = self.test_data
            h_l, n, t = self.net_params
            loss, acc = self.model.evaluate(x.reshape(len(x), 1,10), y, verbose=0)
            with open(STAT_FILE, 'a+') as f:
                f.write('layers: {:}, neurons: {:}, epoch:  {:}, loss: {}, acc: {}\n'.format(h_l, n, epoch, loss, acc))


# splitting the dataset in train and test set
def split_data(x, y, ratio=0.2):
    # converting to numpy array
    x = np.array(x)
    y = np.array(y)

    # splitting dataset in training and testing
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = ratio)
    return x_train, y_train, x_test, y_test


def build_model(x_train, y_train, x_test, y_test, target, hidden_layers=2, neurons=32, epochs=10, plot=True, 
                model_path=None, arch_test=False):

    model = Sequential()
    # model.add(Dense(64, input_shape = (1, 10)))
    # normalizing the input
    model.add(BatchNormalization(input_shape=(1,10)))
    
    # adding the desired number of hidden layers
    for i in range(hidden_layers - 1):
        model.add(LSTM(neurons, dropout=0.3, recurrent_dropout=0.2, return_sequences = True))
    model.add(LSTM(neurons, dropout=0.3, recurrent_dropout=0.2))
    
    model.add(Dense(10, activation='sigmoid', kernel_regularizer=l2(0.01)))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])

    # default batch size = 32
    t0 = time.time()
    
    # flag to check if I'm testing an architecture or training
    if arch_test:
        history = model.fit(x_train.reshape(len(x_train),1,10), y_train, validation_split=0.15, epochs=epochs, verbose=0, 
                        callbacks=[TestCallback((x_test, y_test, hidden_layers, neurons, target))]) 
    else:
        history = model.fit(x_train.reshape(len(x_train),1,10), y_train, validation_split=0.15, epochs=epochs, verbose=0) 

    t1 = time.time()
    
    # if the path is specified, saving the model
    if model_path:
        model.save(model_path)
        
    if plot:
        #print(history.history.keys())
        os.makedirs('plots_final/{:}'.format(target), exist_ok=True)
        
        plt.figure(figsize=(15, 5))
        #  "Accuracy"
        plt.subplot(121)
        plt.plot(history.history['categorical_accuracy'])
        plt.plot(history.history['val_categorical_accuracy'])
        plt.grid()
        plt.title('Model Accuracy')
        plt.ylabel('accuracy')
        plt.xlabel('epoch')
        plt.legend(['Training data', 'Validation data'], loc='lower right')
        # "Loss"
        plt.subplot(122)
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.grid()
        plt.title('Model loss')
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.legend(['Training data', 'Validation data'], loc='upper right')
        plt.savefig('plots_final/plot_{:}.pdf'.format(target))
        plt.close()
        
    loss, acc = model.evaluate(x_test.reshape(len(x_test), 1,10), y_test, verbose=0)
    
    # if testing an architecture, dumping the results to file
    if arch_test:
        with open(STAT_FILE, 'a+') as f:
            f.write('layers: {:}, neurons: {:}, epoch:  {:}, loss: {}, acc: {}, time: {}\n'.format(hidden_layers, neurons, epochs, 
                                                                                     loss, acc, t1-t0))
    
    return history.history, [loss, acc]


def main():
    layers = 2
    neurons = 128
    train_epochs = 150
    targets = os.listdir(MODEL_DIR)
    total = len(targets)
    counter = 0

    for target in targets:
        path = os.path.join(MODEL_DIR, target)
        train_hist = []
        test_metrics = []
        x = []
        y = []
               
        data = os.listdir(path)
        if '{:}_model.h5'.format(target) in data:
            counter+=1
            continue

        print('Training {:} {:}/{:}'.format(target, counter, total))
        # loading the dataset
        for dataset in data:
            file = os.path.join(path, dataset)
            with open(file, 'r') as f:
                lines = f.readlines()
                for line in lines:    
                    cnt, label = line.split(',')
                    cnt = np.array([int(c) for c in cnt.split()[1:]], dtype=np.int)
                    label = np.array([int(l) for l in label.split()], dtype=np.int)
                    x.append(cnt)
                    y.append(label)
            
        x_t, y_t, x_ts, y_ts = split_data(x, y)
        h, m = build_model(x_t, y_t, x_ts, y_ts, target, neurons=neurons, hidden_layers=layers, epochs=train_epochs,
                               plot=True, model_path=os.path.join(path,'{:}_model.h5'.format(target)))
        counter +=1
        print(target, m)
        train_hist.append(h)
        test_metrics.append(m)
         
        # saving the training history and the test metrics    
        with open(os.path.join(path, 'train_hist.pkl'), 'wb') as th:
            pickle.dump(train_hist, th)
            
        with open(os.path.join(path, 'test_metrics.pkl'), 'wb') as tm:
            pickle.dump(test_metrics, tm)


if __name__ == '__main__':
    main()
