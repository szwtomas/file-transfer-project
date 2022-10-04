from .UDPAcceptor import UDPAcceptor
from .sockets.UDPSocket import create_udp_socket
from .user_commands import QUIT, QUIT_ABREVIATED

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
        self.udp_acceptor = UDPAcceptor(self.host, self.port, self.fs_root, self.socket, "saw")
        self.udp_acceptor.start()
        while self.udp_acceptor.is_running():
            user_input = input()
            if user_input == QUIT or user_input == QUIT_ABREVIATED:
                print("Quiting server...")
                break
            else:
                print("Unknown command :(")

        self.udp_acceptor.stop_running()
        self.udp_acceptor.join()