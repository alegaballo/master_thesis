from __future__ import print_function
from keras.models import load_model
from collections import defaultdict
from multiprocessing.connection import Listener
import os
import numpy as np
import my_routes as routes
import time
import random 
import sys
from subprocess import Popen

MODELS_DIR = '/home/mininet/miniNExT/examples/master_thesis/project/trained_models/lstm/'
#MODELS_DIR = '/home/mininet/miniNExT/examples/master_thesis/project/trained_models/dnn/'
ROUTERS_NAMING = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'ri1', 'ri2', 'ri3', 'ri4']

ROUTER_CONF = '/home/mininet/miniNExT/examples/master_thesis/project/configs/interfaces'
SELECTED_T = ['r1_172_168_4_1', 'r2_172_168_4_2', 'r3_172_168_35_1','r4_172_168_35_1', 'r6_172_168_32_1']
SELECTED_T = ['r1_172_168_3_1']

ROUTES = '/home/mininet/miniNExT/examples/master_thesis/project/testing/run0/paths.txt'
ITERATIONS = 1
SAMPLES = 200
TARGETS = os.listdir(MODELS_DIR)
class Predictor(object):
    def __init__(self, *args, **kwargs):
        self.getAddresses(ROUTER_CONF)
        self._load_models()


    def _load_models(self):
        print('Loading models')
        target = [] 
        for i,s in enumerate(SELECTED_T):
            # selecting all the models that take you to that destination
            dst_intf = '_' + '_'.join(s.split('_')[-2:])
            target.extend([t for t in os.listdir(MODELS_DIR) if t.endswith(dst_intf)])
        target = set(target)
        t0=time.time()
        self.models = {t:get_model(t) for t in target}
        t1=time.time()
        print('Models loaded: loading time {:} s'.format(t1-t0))


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
            if len(path) > 10:
                print('!!!DETECTED LOOP')
                return -1
            
            target = '{:}_{:}'.format(src, dst_addr.replace('.', '_'))
            model = self.models[target]
            predictions = model.predict(counter)
            next_router = ROUTERS_NAMING[np.argmax(predictions)]
            path.append(next_router)
            src = next_router
        print('Predicted path:\t{:}'.format(path))
        return path


def get_model(target):
    model_dir = os.path.join(MODELS_DIR, target)
    
    print('Loading model: {:} ...'.format(target), end='\t')
    model = load_model(model_dir + '/{:}_model.h5'.format(target))
    print('[DONE]')
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
        return route


def print_route(route):
    target, hops = route.split(':')
    hops = hops.strip().split()
    path = [ROUTERS_NAMING[int(h)] for h in hops]
    print('OSPF path:\t{:}'.format(path))
    

# select a random target
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
    #ryu=Popen(['ryu-manager', 'testSwitch.py'])
    print('waiting for connections')
    conn = listener.accept()
    print('new connection from {:}'.format(listener.last_accepted))
    with open('mininet_dump', 'w+') as mn:

        #mininet=Popen(['python', 'test_net.py'], cwd='/home/mininet/miniNExT/examples/master_thesis/project/', stdout=mn, stderr=mn)
        k = 0
        iteration = 0
        with open(sys.argv[1], 'w+') as f:
            while iteration < ITERATIONS:
                if os.path.isfile(ROUTES):
                    print('Predictions started')
                    with open(ROUTES, 'r') as r:
                        routes = r.readlines()
                    paths = [line.strip() for line in routes]
                    while k < SAMPLES:
                        msg = conn.recv()
                        cnt = np.array(msg[1:]).reshape(1,1,10)
                        if sum(cnt[0][0] > 10):
                            # predicting all the paths
                            for t in SELECTED_T:
                                target= t.split('_')
                                src = target[0]
                                dst = '.'.join(target[1:])
                                predicted = pr.predict(src, dst, cnt)
                                ospf = get_ospf(paths, src, dst)
                                if predicted and ospf:
                                    ospf = ospf.split(':')[1].strip().split()
                                    ospf = [ROUTERS_NAMING[int(h)] for h in ospf]
                                    f.write(t + '\n')
                                    f.write(str(cnt[0][0])+'\n')
                                    f.write('prediction:'+str(predicted)+'\n')
                                    f.write('ospf:'+str(ospf)+'\n')
                                    k += 1
                                    print('{:}/{:}'.format(k, 200*len(SELECTED_T)))
                    print('*****************FINISH RUN******************')
                    os.remove(ROUTES)
                    k = 0
                    iteration +=1
                    
                else:
                    time.sleep(2)
#    ryu.terminate()
#    mininet.terminate()
    listener.close()


       
