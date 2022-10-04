from socket import timeout
from .UDPConnection import UDPConnection
import threading

ACCEPT_TIMEOUT_IN_SECONDS = 0.5
MAX_BUF_SIZE = 4096

class UDPAcceptor(threading.Thread):

    def __init__(self, host, port, fs_root, socket):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.fs_root = fs_root
        self.socket = socket
        self.connections = {}


    def run(self):
        print("UDP Acceptor running")
        print(f"UDP Acceptor socket timeout set to: {ACCEPT_TIMEOUT_IN_SECONDS} seconds")
        while True:
            try:
                self.socket.settimeout(ACCEPT_TIMEOUT_IN_SECONDS)
                data, client_address = self.socket.recvfrom(MAX_BUF_SIZE)
            except timeout:
                print("UDP Acceptor timeouted")
                continue

            self.create_connection_if_not_exists(client_address)
            self.connections[client_address].enqueue_message(data)
            print(f"Enqueued to connection of address: {client_address} , message of bytes: {data[:16]}")

            self.remove_dead_connections()


    def create_connection_if_not_exists(self, client_address):
        if client_address not in self.connections:
            self.connections[client_address] = UDPConnection(client_address, self.socket, self.fs_root)
            self.connections[client_address].start()


    def remove_dead_connections(self):
        # TODO: Iterate all connections and check last message time and remove dead connections or something
        return True
