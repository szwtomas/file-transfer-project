from socket import socket

# This is the parent class, so methods should not be implemented here
class Socket:

    def accept(self) -> tuple:
        return self.socket.accept()

    def read_data(self):
        pass