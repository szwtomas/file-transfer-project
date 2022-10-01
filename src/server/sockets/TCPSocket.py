from socket import socket

RECV_CHUNK_SIZE = 1024

class TCPSocket:

    def __init__(self, socket):
        self.socket = socket


    def read_data(self):
        return self.socket.recv(RECV_CHUNK_SIZE)


    def send_data(self, data):
        self.socket.send(data)


    def close(self):
        self.socket.close()

