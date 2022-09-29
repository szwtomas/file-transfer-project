from socket import socket

# This is the parent class, so methods should not be implemented here
class Socket:

    def accept(self) -> tuple:
        pass

    def read_data(self):
        pass

    def send_data(self, data):
        pass