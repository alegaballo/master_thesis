import protobuf.messages_pb2 as msg_pb2
import socket
import sys
import time

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# creating a new offloading request message
message = msg_pb2.Message()
message.off_req.type = msg_pb2.OffloadRequest.STANDARD
message.off_req.requirements.cpu = 0.5
message.off_req.requirements.memory = 50
message.off_req.requirements.latency = msg_pb2.OffloadRequest.Requirements.URGENT
message.off_req.task.wrapper.name = 'task 1'
message.off_req.task.wrapper.type = msg_pb2.OffloadRequest.Task.TaskWrapper.JAR

# random sample to test the ability of sending a file
with open('test.pdf','rb') as f:
    message.off_req.task.wrapper.task = f.read()

size = message.ByteSize()
print('Message size: {:} bytes'.format(size))

# sending the message over the socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(str(size) + "\n", "utf-8"))
    answer_s = sock.recv(1024)
    answer = msg_pb2.Message()
    answer.ParseFromString(answer_s)
    print(answer)
    sock.sendall(message.SerializeToString())
    # Receive data from the server and shut down
    received = str(sock.recv(1024), "utf-8")
