from socket import timeout
from .UDPConnection import UDPConnection
import threading

ACCEPT_TIMEOUT_IN_SECONDS = 0.5
MAX_BUF_SIZE = 4096

class UDPAcceptor(threading.Thread):

    def __init__(self, host, port, fs_root, socket, protocol):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.fs_root = fs_root
        self.socket = socket
        self.connections = {}
        self.protocol = protocol
        self.should_run = True


    def run(self):
        print("UDP Acceptor running")
        print(f"UDP Acceptor socket timeout set to: {ACCEPT_TIMEOUT_IN_SECONDS} seconds")
        self.should_run = True
        while self.should_run:
            try:
                self.socket.settimeout(ACCEPT_TIMEOUT_IN_SECONDS)
                data, client_address = self.socket.recvfrom(MAX_BUF_SIZE)
            except timeout:
                continue

            self.create_connection_if_not_exists(client_address)
            self.connections[client_address].enqueue_message(data)
            print(f"Enqueued to connection of address: {client_address} , message of bytes: {data[:16]}")

            number_of_connections_killed = self.remove_dead_connections()
            print(f"{number_of_connections_killed} where killed")

        self.close_connections()
        self.socket.close()
        

    def create_connection_if_not_exists(self, client_address):
        if client_address not in self.connections:
            self.connections[client_address] = UDPConnection(client_address, self.socket, self.fs_root, self.protocol)
            self.connections[client_address].start()


    def close_connections(self):
        for conn in self.connections:
            self.connections[conn].join()


    def is_running(self):
        return self.should_run


    def stop_running(self):
        self.should_run = False


    def remove_dead_connections(self):
        connections_to_kill = []
        try:
            
            for conn_addr in self.connections:
                if not self.connections[conn_addr].is_alive():
                    connections_to_kill.append(conn_addr)

            for conn_addr in connections_to_kill:
                print(f"Connection for client with address: {conn_addr} is dead, removing it")
                del self.connections[conn_addr]
        except Exception as e:
            print("Failed to remove dead connection")

        return len(connections_to_kill)


