from keras.models import load_model
from collections import defaultdict
from multiprocessing.connection import Listener
import os
import numpy as np
import my_routes as routes
import time
import random 
MODELS_DIR = '/home/mininet/miniNExT/examples/master_thesis/project/models_final/'
ROUTERS_NAMING = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'ri1', 'ri2', 'ri3', 'ri4']

ROUTER_CONF = '/home/mininet/miniNExT/examples/master_thesis/project/configs/interfaces'
#TARGET = 'r1_172_168_4_1'
#PATH = 'r1 172.168.4.1:'
DST_INTF = '_2_2'
ROUTES = '/home/mininet/miniNExT/examples/master_thesis/project/testing/run0/paths.txt'

TARGETS = os.listdir(MODELS_DIR)
class Predictor(object):
    def __init__(self, *args, **kwargs):
        self.getAddresses(ROUTER_CONF)
        self._load_models()


    def _load_models(self):
        print('Loading models')
        target = [t for t in os.listdir(MODELS_DIR) if t.endswith(DST_INTF)]
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
        counter = np.array(counter).reshape((1,1,10))
        print(counter)
        while True:
            if dst_addr in self.addresses[src]:
                break
            target = '{:}_{:}'.format(src, dst_addr.replace('.', '_'))
            model = self.models[target]
            predictions = model.predict(counter)
            next_router = ROUTERS_NAMING[np.argmax(predictions)]
            path.append(next_router)
            src = next_router
        print('Predicted path:\t{:}'.format(path))

def get_model(target):
    model_dir = os.path.join(MODELS_DIR, target)
    model = load_model(model_dir + '/{:}_model.h5'.format(target))
    #model._make_predict_function()
    return model

def get_ospf(paths, src, dst):
    if not paths:
        if os.path.isfile(ROUTES):
            with open(ROUTES,'r') as f:
                routes = f.readlines()
            paths.extend([line.strip() for line in routes])
    else:
        route = [p for p in paths if '{:} {:}:'.format(src, dst) in p][0]
        print_route(route)

def print_route(route):
    target, hops = route.split(':')
    hops = hops.strip().split()
    path = [ROUTERS_NAMING[int(h)] for h in hops]
    print('OSPF path:\t{:}'.format(path))


def get_target():
    target = TARGETS[random.randint(0, len(TARGETS))]
    print(target)
    t = target.split('_')
    src = t[0]
    dst = '.'.join(t[1:])
    return src, dst   


if __name__=='__main__':
    try:
        os.remove(ROUTES)
    except:
        pass
    paths = []
    pr = Predictor()
    adr = ('localhost', 6000)
    listener = Listener(adr, authkey='hola')
    conn = listener.accept()
    print('new connection from {:}'.format(listener.last_accepted))
    while True:
        msg=conn.recv()
        cnt = np.array(msg[1:]).reshape(1,1,10)
        #src, dst = get_target()
        src = 'r1'
        dst = '172.168.2.2'
        pr.predict(src, dst, cnt)
        get_ospf(paths, src, dst)
    
    listener.close()


       
