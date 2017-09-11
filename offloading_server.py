import protobuf.messages_pb2 as msg_pb2
import sys
import socketserver


MESSAGE_TYPES = {'offload_request': msg_pb2.OffloadRequest()}


class MyTCPHandler(socketserver.StreamRequestHandler):
    def handle(self, *args):

        message = self.read_message()
        print("{} wrote:".format(self.client_address[0]))
        print(message)
        # self.server.ryu_app.send_event_to_observers(EventMsg('New Policy request'))
        # just send back the same data, but upper-cased
        self.data = bytes('ciao', 'utf-8')
        self.request.sendall(self.data.upper())

    def send_message(self, message):
        size = str(message.ByteSize())
        self.request.sendall(bytes(size + '\n'))
        self.request.sendall(message.SerializeToString())

    def read_message(self):
        self.data = self.rfile.readline().strip()
        try:
            msg_size = int(self.data)
        except ValueError:
            print('not a valid message size')
            # send error message

        print('Expected message size', msg_size)
        self.request.sendall(bytes('OK\n', 'utf-8'))
        received = 0
        message_s = bytes()
        while received != msg_size:
            message_s += self.request.recv(msg_size - received)
            received = len(message_s)

        print('Received message size: {:}'.format(len(message_s)))
        message = MESSAGE_TYPES['offload_request']
        message.ParseFromString(message_s)

        return message


def main():
    HOST, PORT = "localhost", 9996
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()