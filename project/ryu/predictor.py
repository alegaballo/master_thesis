from keras.models import load_model
from collections import defaultdict
from multiprocessing.connection import Listener
import os
import numpy as np


MODELS_DIR = '/home/mininet/miniNExT/examples/master_thesis/project/models_final/'
ROUTERS_NAMING = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'ri1', 'ri2', 'ri3', 'ri4']

ROUTER_CONF = '/home/mininet/miniNExT/examples/master_thesis/project/configs/interfaces'


class Predictor(object):
    def __init__(self, *args, **kwargs):
        self.getAddresses(ROUTER_CONF)
        self._load_models()


    def _load_models(self):
        print('Loading models')
        target = [t for t in os.listdir(MODELS_DIR) if t.endswith('_3_2')]
        self.models = {t:get_model(t) for t in target }
        print('Models loaded')


    def getAddresses(self, conf_file):
        self.addresses=defaultdict(list)
        with open(conf_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    router, interface, address = line.split()
                    self.addresses[router].append(address)

    
    def predict(self, src, dst_addr, counter):
        path = [src]
        counter = np.zeros((1,1,10))

        while True:
            if dst_addr in self.addresses[src]:
                break
            target = '{:}_{:}'.format(src, dst_addr.replace('.', '_'))
            model = self.models[target]
            predictions = model.predict(counter)
            next_router = ROUTERS_NAMING[np.argmax(predictions)]
            path.append(next_router)
            src = next_router
        print(path)

def get_model(target):
    model_dir = os.path.join(MODELS_DIR, target)
    model = load_model(model_dir + '/{:}_model.h5'.format(target))
    #model._make_predict_function()
    return model


pr = Predictor()
adr = ('localhost', 6000)
listener = Listener(adr, authkey='hola')
conn = listener.accept()
print('new connection from {:}'.format(listener.last_accepted))
while True:
    msg=conn.recv()
    cnt = np.array(msg[1:]).reshape(1,1,10)
    pr.predict('r1','172.168.3.2', cnt)
listener.close()


       
