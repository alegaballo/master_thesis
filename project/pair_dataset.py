import os
import re
import numpy as np

DATASET = './dataset/'

def make_dir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)


# for all the different run
for run in os.listdir(DATASET):
    dir_content = os.listdir(os.path.join(DATASET, run))
    # getting the capture file
    for content in dir_content:
        if 'capture' in content:
            capture = content
    with open(os.path.join(DATASET, run, capture), 'r')as cap_f:
        #do something
        counters = cap_f.readlines()
        # reading all the paths associated to that run
        with open(os.path.join(DATASET, run, 'paths.txt'), 'r') as f:
            # creating a folder for every src,dst pair
            for line in f:
                target, path = line.strip().split(':')
                target = re.sub('[ .]+', '_', target)
                folder = os.path.join('./models', target)
            
                make_dir(folder)
                # creating a folder for each router traversed in the path between src,dst without considering the last hop
                path = [int(hop) for hop in path.split()]
                for i,router in enumerate(path[:-1]):
                    model_folder = os.path.join(folder, 'r{:}'.format(router+1))
                    make_dir(model_folder)
                    label = np.zeros(10, dtype=np.int)
                    label[path[i+1]]=1
                    dataset_file = 'dataset_{:}'.format(run)
                    with open(os.path.join(model_folder, dataset_file), 'w+') as f:
                        label = ' '.join(str(i) for i in label)+'\n'
                        for counter in counters:
                            line = counter.strip() + ', ' + label
                            f.write(line)


