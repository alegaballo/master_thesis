import socket
import socketserver


class TCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        msg_size = self.rfile.readline().strip()
        print(msg_size)
        try:
            msg_size = int(msg_size)
        except ValueError:
            # send error response
            print(' ehhhhhhhhh volevi')
            return

    def read_message(self, msg_size):
        pass


if __name__ == "__main__":
    HOST, PORT = 'localhost', 9998
    server = socketserver.ThreadingTCPServer((HOST, PORT), TCPHandler)
    server.serve_forever()