from constants import CHUNK_SIZE, LOCALHOST, PORT, SOCKET_MAX_QUEUE
from socket import socket, AF_INET, SOCK_STREAM
from Socket import Socket

class TCPSocket(Socket):
    
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((LOCALHOST, PORT))
        self.socket.listen(SOCKET_MAX_QUEUE)


    def accept(self) -> tuple:
        return self.socket.accept()

    def read_data(self, bytes_to_read: int) -> bytes: #FIXME: should we use CHUNK_SIZE?
        return self.socket.recv(bytes_to_read)

    def send_data(self, data):
        self.socket.send(data)
