from socket import socket as create_socket, AF_INET, SOCK_STREAM

RECV_CHUNK_SIZE = 1024

def create_tcp_socket():
    return create_socket(AF_INET, SOCK_STREAM)

class TCPSocket:

    def __init__(self, socket):
        self.socket = socket


    def read_data(self, chunk_size=RECV_CHUNK_SIZE):
        return self.socket.recv(chunk_size)


    def send_data(self, data):
        self.socket.send(data)


    def close(self):
        self.socket.close()

