from constants import LOCALHOST, PORT, SOCKET_MAX_QUEUE
from socket import socket, AF_INET, SOCK_STREAM
from Socket import Socket

class TCPSocket(Socket):
    
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((LOCALHOST, PORT))
        self.socket.listen(SOCKET_MAX_QUEUE)


    def accept(self) -> tuple:
        return self.socket.accept()