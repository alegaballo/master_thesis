previous = ''
accuracies = []
losses = []
times = []
with open('final', 'r') as f:
    for line in f:
        layer, neurons, epoch, loss, acc, timing  = line.strip().split(',')
        arch = layer + neurons
        accuracy = float(acc.split()[1])
        loss_ = float(loss.split()[1])
        time = float(timing.split()[1])
        if arch != previous and previous:
            #print('{:} accuracy: {:} samples: {:}'.format(previous, sum(accuracies)/float(len(accuracies)), len(accuracies)))
            avg_acc = sum(accuracies)/float(len(accuracies))
            avg_loss = sum(losses)/float(len(losses))
            avg_time = sum(times)/float(len(times))
            score = (avg_acc + 1/avg_loss)/avg_time
            print('{:} accuracy: {:} loss: {:} time: {:} score {:} samples: {:}'.format(previous, avg_acc, avg_loss, avg_time, score, len(accuracies)))
            accuracies = []
            losses = []
            times = []
        accuracies.append(accuracy)
        losses.append(loss_)
        times.append(time)
        previous = arch

avg_acc = sum(accuracies)/float(len(accuracies))
avg_loss = sum(losses)/float(len(losses))
avg_time = sum(times)/float(len(times))
score = avg_acc + 1/avg_loss + 1/avg_time
print('{:} accuracy: {:} loss: {:} time: {:} score {:} samples: {:}'.format(previous, avg_acc, avg_loss, avg_time, score, len(accuracies)))

