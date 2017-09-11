import protobuf.messages_pb2 as msg_pb2
import socket
import sys
import time

HOST, PORT = "localhost", 9996
data = " ".join(sys.argv[1:])

message = msg_pb2.OffloadRequest()
message.type = msg_pb2.OffloadRequest.STANDARD
message.requirements.cpu = 0.5
message.requirements.memory = 50
message.requirements.latency = msg_pb2.OffloadRequest.Requirements.URGENT
message.task.wrapper.name = 'task 1'
message.task.wrapper.type = msg_pb2.OffloadRequest.Task.TaskWrapper.JAR
with open('test.pdf','rb') as f:
    message.task.wrapper.task = f.read()
size = message.ByteSize()
print('Message size: {:} bytes'.format(size))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(str(size) + "\n", "utf-8"))
    print(sock.recv(1024).strip())
    sock.sendall(message.SerializeToString())
    # Receive data from the server and shut down
    received = str(sock.recv(1024), "utf-8")

print("Sent:     {}".format(message))
print("Received: {}".format(received))
