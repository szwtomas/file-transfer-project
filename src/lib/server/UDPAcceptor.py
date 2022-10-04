from socket import timeout
import threading
from .UDPConnection import UDPConnection
from .constants import ACCEPT_TIMEOUT_IN_SECONDS, MAX_BUF_SIZE


class UDPAcceptor(threading.Thread):

    def __init__(self, host, port, fs_root, socket, protocol):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.fs_root = fs_root
        self.socket = socket
        self.connections = {}
        self.protocol = protocol


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
            self.remove_dead_connections()


    def remove_dead_connections(self):
        for conn in self.connections:
            if not self.connections[conn].is_alive():
                print(f"KILLING CONNECTION OF ADDRESS: {conn}")
                del self.connections[conn]


    def stop_running(self):
        self.stop_all_connections()
        self.connections = {}
        self.socket.close()


    def create_connection_if_not_exists(self, client_address):
        if client_address not in self.connections:
            self.connections[client_address] = UDPConnection(client_address, self.socket, self.fs_root, self.protocol)
            self.connections[client_address].start()

