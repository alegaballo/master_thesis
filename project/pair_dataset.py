import os
import re
import numpy as np

DATASET = './dataset_final/'

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
            break

    cap_file = os.path.join(DATASET, run, capture)
    print(cap_file)
    with open(cap_file, 'r') as cap_f:
        #do something
        counters = cap_f.readlines()
        # reading all the paths associated to that run
        with open(os.path.join(DATASET, run, 'paths.txt'), 'r') as path_f:
            # creating a folder for every src,dst pair
            for line in path_f:
                target, path = line.strip().split(':')
                target = re.sub('[ .]+', '_', target)
                folder = os.path.join('./models_final', target)

                make_dir(folder)
                path = [int(hop) for hop in path.split()]
                next_hop = path[1]
                label = np.zeros(10, dtype=np.int)
                label[next_hop] = 1
				# writing the dataset in the final form: packet_counter, next_hop
                dataset_file = 'dataset_final{:}'.format(run)
                with open(os.path.join(folder, dataset_file), 'w+') as f:
                    label = ' '.join(str(i) for i in label)+'\n'
                    for counter in counters:
                        line = counter.strip() + ', ' + label
                        f.write(line)

