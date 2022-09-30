from socket import socket, AF_INET, SOCK_STREAM
from Server import Server
from server.src.sockets.TCPSocket import TCPSocket

class TCPServer(Server):

    def __init__(self, port):
        super().__init__(port)
        self.socket = TCPSocket()

                        
    def get_connection(self):
        return self.socket.accept()
