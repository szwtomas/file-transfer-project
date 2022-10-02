import threading
from socket import timeout
from .TCPConnection import TCPConnection
from .sockets.TCPSocket import TCPSocket, create_tcp_socket

ACCEPT_TIMEOUT_IN_SECONDS = 3

class Acceptor(threading.Thread):
    
    def __init__(self, host, port, fs_root):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.connections = {}
        self.fs_root = fs_root
        self.socket = None
        self.should_run = True
        
    def run(self):
        print("Acceptor started running")
        self.socket = create_tcp_socket()
        listen_address = (self.host, self.port)
        self.socket.bind(listen_address)
        self.socket.listen()
        print(f"Acceptor listening on address: {listen_address}")
        self.socket.settimeout(ACCEPT_TIMEOUT_IN_SECONDS)
        print(f"Acceptor socket timeout set to: {ACCEPT_TIMEOUT_IN_SECONDS} seconds")
        try:
            while self.should_run:
                print("Acceptor waiting for incoming connection...")
                try:
                    client_socket, client_address = self.socket.accept()
                except timeout:
                    print("Acceptor timeouted")
                    continue
                tcp_socket = TCPSocket(client_socket)
                self.connections[client_address] = TCPConnection(tcp_socket, self.fs_root)
                self.connections[client_address].start()
        except Exception as e:
            print(f"Error: {e}")
        

    def stop_running(self):
        self.socket.close()
        print("Acceptor socket closed")
        for connection in self.connections:
            print(f"Closing connection: {connection}")
            self.connections[connection].stop_running()
            self.connections[connection].join()
        self.should_run = False

        
