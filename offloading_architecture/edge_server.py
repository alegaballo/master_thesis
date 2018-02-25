import protobuf.messages_pb2 as msg_pb2
import socketserver

RESPONSES = {'OK': msg_pb2.Response.OK, 'INVALID_SIZE': msg_pb2.Response.INVALID_MSG_SIZE,
             'INVALID_REQUEST': msg_pb2.Response.INVALID_REQUEST}


class TCPHandler(socketserver.StreamRequestHandler):
    def setup(self):
        # calling superclass method which initialize rfile
        super(TCPHandler, self).setup()
        self.SEND_MSGS = {'response': self.send_response}

    def handle(self):
        message = self.read_message()

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
		# sending confirmation of the message receipt, necessary for some troubles with python sockets
        self.send_message('response', response=RESPONSES['OK'], msg='OK')

        return self.receive_message(msg_size)

    
	# receives a message of the specified size	
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

    def send_message(self, MESSAGE_TYPE, **kwargs):
        self.SEND_MSGS[MESSAGE_TYPE](**kwargs)
    

	def send_response(self, **kwargs):
        msg = msg_pb2.Message()
        msg.type = msg_pb2.Message.RESPONSE
        msg.response.result = kwargs['response']
        msg.response.msg = kwargs['msg']
        self.request.sendall(msg.SerializeToString())


if __name__ == "__main__":
    HOST, PORT = 'localhost', 9998
    server = socketserver.ThreadingTCPServer((HOST, PORT), TCPHandler)
    server.serve_forever()
