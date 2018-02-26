
# coding: utf-8

# In[1]:

from keras.models import Sequential
from keras.layers import Dense, BatchNormalization
from keras.regularizers import l2
from keras.callbacks import Callback
from pandas import DataFrame
import numpy as np
import pickle
import matplotlib.pyplot as plt
import time
import os
from sklearn.model_selection import train_test_split
MODEL_DIR = './../models_final/'
TRAINED_MODEL_DIR = './../trained_models/dnn/'


# In[2]:

layers = 4
neurons = 16
epochs = 128


# In[3]:

def build_model(layers=4, neurons=16):
    model = Sequential()
    model.add(BatchNormalization(input_shape=(1,10)))

    for i in range(layers):
        model.add(Dense(neurons))

    model.add(Dense(10, activation='sigmoid', kernel_regularizer=l2(0.01)))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
    return model

def split_data(x, y, ratio=0.2):
    # converting to numpy array
    x = np.array(x)
    y = np.array(y)
    
    # splitting dataset in training and testing
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = ratio)
    return x_train, y_train, x_test, y_test


# In[8]:

targets = os.listdir(MODEL_DIR)
trained = 1
for target in targets:
    print('Training {:}/{:} ...'.format(trained ,len(targets)))
    path = os.path.join(MODEL_DIR, target)
    train_hist = []
    test_metrics = []
    x = []
    y = []
    out_path = os.path.join(TRAINED_MODEL_DIR, target)
    for dataset in os.listdir(path):
        file = os.path.join(path, dataset)
        if 'dataset' not in file:
            continue
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:    
                cnt, label = line.split(',')
                cnt = np.array([int(c) for c in cnt.split()[1:]], dtype=np.int)
                label = np.array([int(l) for l in label.split()], dtype=np.int)
                x.append(cnt)
                y.append(label)
        
    x_t, y_t, x_ts, y_ts = split_data(x, y)
    model = build_model()
    history = model.fit(x_t.reshape(len(x_t),1,10), y_t.reshape(len(y_t), 1, 10), 
                        validation_split=0.15, epochs=epochs, verbose=0) 
    loss, acc = model.evaluate(x_ts.reshape(len(x_ts), 1, 10), y_ts.reshape(len(y_ts), 1, 10), verbose=0)
    os.makedirs(out_path, exist_ok=True) 
    
    model.save(os.path.join(out_path, '{:}_model.h5'.format(target)))
    with open(os.path.join(out_path, 'train_hist.pkl'), 'wb') as th:
        pickle.dump(history.history, th)

    with open(os.path.join(out_path, 'test_metrics.pkl'), 'wb') as tm:
        pickle.dump([loss, acc], tm)
    
    print(target, acc)
    trained += 1


# In[ ]:



