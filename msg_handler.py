import os
import socketserver
from ryu.base import app_manager
from ryu.controller import event
from ryu.lib import hub

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self, *args):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        self.server.ryu_app.send_event_to_observers(EventMsg('New Policy request'))
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())
        
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

