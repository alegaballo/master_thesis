import  protobuf.messages_pb2 as msg_pb2
import socket
import sys

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
msg = msg_pb2.OffloadRequest()
msg.type = msg_pb2.OffloadRequest.LAMBDA
msg.requirements.cpu = 0.5
msg.requirements.memory = 50
msg.requirements.latency = msg_pb2.OffloadRequest.Requirements.URGENT
msg.task.wrapper.name = 'task 1'
msg.task.wrapper.type = msg_pb2.OffloadRequest.Task.TaskWrapper.JAR
with open('sample.txt', 'rb') as f:
	jar = f.read()
print(type(jar))
msg.task.wrapper.task = jar
srz = msg.SerializeToString()
size = msg.ByteSize()
print(msg.ByteSize())
# req.requirements = req
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(str(size) + "\n", "utf-8"))
    sock.sendall(srz)
    # Receive data from the server and shut down
    received = str(sock.recv(1024), "utf-8")

print("Sent:     {}".format(data))
print("Received: {}".format(received))
