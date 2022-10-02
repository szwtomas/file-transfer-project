from server.Acceptor import ACCEPT_TIMEOUT_IN_SECONDS
from socket import timeout
from UDPConnection import UDPConnection

ACCEPT_TIMEOUT_IN_SECONDS = 3
MAX_BUF_SIZE = 1024

class UDPAcceptor:

    def __init__(self, host, port, fs_root, socket):
        self.host = host
        self.port = port
        self.fs_root = fs_root
        self.socket = socket
        self.connections = {}


    def run(self):
        print("UDP Acceptor running")
        self.socket.settimeout(ACCEPT_TIMEOUT_IN_SECONDS)
        print(f"UDP Acceptor socket timeout set to: {ACCEPT_TIMEOUT_IN_SECONDS} seconds")
        while True:
            try:
                data, client_address = self.socket.recvfrom(MAX_BUF_SIZE)
            except timeout:
                print("UDP Acceptor timeouted")
                continue

            self.create_connection_if_not_exists(client_address)
            self.connections[client_address].enqueue_message(data)
            print(f"Enqueued to connection of address: {client_address} , message of bytes: {data}")

            self.remove_dead_connections()


    def create_connection_if_not_exists(self, client_address):
        if client_address not in self.connections:
            self.connections[client_address] = UDPConnection(self.socket, self.fs_root)
            self.connections[client_address].start()


    def remove_dead_connections(self):
        # TODO: Iterate all connectiond and check last message time and remove dead connections or something
        return True