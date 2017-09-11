import protobuf.messages_pb2 as msg_pb2
import sys
import socketserver


MESSAGE_TYPES = {'offload_request': msg_pb2.OffloadRequest()}
RESPONSES = {'OK': msg_pb2.Response.OK, 'INVALID_SIZE': msg_pb2.Response.INVALID_MSG_SIZE,
             'INVALID_REQUEST': msg_pb2.Response.INVALID_REQUEST}


class MyTCPHandler(socketserver.StreamRequestHandler):
    def setup(self):
        # calling superclass method which initialize rfile
        super(MyTCPHandler, self).setup()
        self.SEND_MSGS = {'response': self.send_response}

    def handle(self, *args):
        message = self.read_message()
        if message:
            print("{} wrote:".format(self.client_address[0]))
            print(message)

            # need to scan msg content

    def send_message(self, MESSAGE_TYPE, **kwargs):
        self.SEND_MSGS[MESSAGE_TYPE](**kwargs)

    def send_response(self, **kwargs):
        msg = msg_pb2.Message()
        msg.type = msg_pb2.Message.RESPONSE
        msg.response.result = kwargs['response']
        msg.response.msg = kwargs['msg']
        self.request.sendall(msg.SerializeToString())

    def receive_message(self, msg_size):
        received = 0
        message_s = bytes()
        while received != msg_size:
            message_s += self.request.recv(msg_size - received)
            received = len(message_s)

        print('Received message size: {:}'.format(len(message_s)))
        message = msg_pb2.Message()
        message.ParseFromString(message_s)

        return message

    def read_message(self):
        # reading incoming message size
        self.data = self.rfile.readline().strip()

        try:
            msg_size = int(self.data)
        except ValueError:
            print('not a valid message size')
            self.send_message('response', response=RESPONSES['INVALID_SIZE'], msg='{:} is not a valid msg size'.format(self.data))
            return
            # send error message
        message = msg_pb2.Message()
        print('Expected message size', msg_size)
        self.send_message('response', response=RESPONSES['OK'], msg='OK')

        return self.receive_message(msg_size)


def main():
    HOST, PORT = "localhost", 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
