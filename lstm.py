from keras.models import Sequential
from keras.layers import Dense, Recurrent, LSTM
from pandas import DataFrame
import numpy as np
import os
from sklearn.model_selection import train_test_split


MODEL_DIR = './project/models/'


def print_samples(x, y, n=10):
    higher = len(x)
    print(higher)
    for i in range(n):
        j = np.random.randint(0, higher)
        print(x[j], y[j])


def build_model(x, y):
    # converting to numpy array
    x = np.array(x)
    y = np.array(y)
    
    # splitting dataset in training and testing
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)


    model = Sequential()
    #model.add(Dense(64, input_shape = (1, 10)))
    model.add(LSTM(64, return_sequences = True, input_shape=(1,10)))
    model.add(LSTM(64))
    model.add(Dense(10    , activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
    metrics=['accuracy'])

    model.fit(x_train.reshape(len(x_train),1,10), y_train, validation_split=0.1) 
    x = model.evaluate(x_test.reshape(len(x_test), 1,10), y_test)
    print('Done')


for target in os.listdir(MODEL_DIR):
    path = os.path.join(MODEL_DIR, target)
    print(target)
    for router in os.listdir(path):
        model = os.path.join(path, router)
        x = []
        y = []
        for dataset in os.listdir(model):
            file = os.path.join(model, dataset)
            with open(file, 'r') as f:
                lines = f.readlines()
            for line in lines:    
                cnt, label = line.split(',')
                cnt = np.array([int(c) for c in cnt.split()[1:]], dtype=np.int)
                label = np.array([int(l) for l in label.split()], dtype=np.int)
                x.append(cnt)
                y.append(label)
        
        build_model(x, y)

        break
    break
 
