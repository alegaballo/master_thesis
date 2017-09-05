import  protobuf.messages_pb2 as msg_pb2
import os
import socketserver
from ryu.base import app_manager
from ryu.controller import event
from ryu.lib import hub

MESSAGE_TYPES = {'offload_request': msg_pb2.OffloadRequest()}

class MyTCPHandler(socketserver.StreamRequestHandler):
    def handle(self, *args):
        message = self.read_message()
        print("{} wrote:".format(self.client_address[0]))
        print(message)
        self.server.ryu_app.send_event_to_observers(EventMsg('New Policy request'))
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

    def send_message(self, message):
        size = string(message.ByteSize())
        self.request.sendall(bytes(size + '\n'))
        self.request.sendall(message.SerializeToString())

    def read_message(self,):
        self.data = self.rfile.readline().strip()

        try:
            msg_size = int(self.data)
        except ValueError:
            print('not a valid message size')

        message_s = self.request.recv(msg_size)
        message = MESSAGE_TYPES['offload_request']
        message.MergeFromString(message_s)
        return message
        
class EventMsg(event.EventBase):
    def __init__(self, msg):
        super(EventMsg, self).__init__()
        self.msg = msg

class MessageHandler(app_manager.RyuApp):
    _EVENTS = [EventMsg]
    
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)

    def start(self):
        super(MessageHandler, self).start()
        self.threads.append(hub.spawn(self.listen   ))
        
    def listen(self):
        HOST, PORT = "localhost", 9999
        server = socketserver.TCPServer((HOST, PORT), MyTCPHandler, 'ciao')
        server.ryu_app = self
        server.serve_forever()

