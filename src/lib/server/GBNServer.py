from .UDPAcceptor import UDPAcceptor
from .sockets.UDPSocket import create_udp_socket
from .user_commands import QUIT, QUIT_ABREVIATED

class GBNServer:

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
        self.udp_acceptor = UDPAcceptor(self.host, self.port, self.fs_root, self.socket, "gbn")
        self.udp_acceptor.start()
        while True:
            user_command = input()
            if user_command == QUIT or user_command == QUIT_ABREVIATED:
                self.handle_quit()    
                break
            else:
                print("Unknown command :(")


    def handle_quit(self):
        print("Server stopping")
        self.udp_acceptor.stop_running()
        print("About to join acceptor thread")
        self.udp_acceptor.join()
        print("Acceptor thread joined")
