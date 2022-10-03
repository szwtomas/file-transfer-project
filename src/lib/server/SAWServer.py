from .UDPAcceptor import UDPAcceptor
from .sockets.UDPSocket import create_udp_socket

class SAWServer():

    def __init__(self, host, port, fs_root, ):
        self.host = host
        self.port = port
        self.fs_root = fs_root
        self.udp_message_sender = None
        self.udp_acceptor = None
        self.socket = None

    def run(self):
        self.socket = create_udp_socket()
        address = (self.host, self.port)
        self.socket.bind(address)
        self.udp_acceptor = UDPAcceptor(self.host, self.port, self.fs_root, self.socket)
        self.udp_acceptor.start()