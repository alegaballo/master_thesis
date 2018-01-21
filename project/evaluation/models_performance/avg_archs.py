previous = ''
accuracies = []
with open('final', 'r') as f:
    for line in f:
        layer, neurons, epoch, loss, acc = line.strip().split(',')[:-1]
        arch = layer + neurons
        accuracy = float(acc.split()[1])
        if arch != previous and previous:
            print('{:} accuracy: {:} samples: {:}'.format(previous, sum(accuracies)/float(len(accuracies)), len(accuracies)))
            accuracies = []

        accuracies.append(accuracy)
        previous = arch

print('{:} accuracy: {:} samples: {:}'.format(previous, sum(accuracies)/float(len(accuracies)), len(accuracies)))

