import threading
from socket import timeout
from .TCPConnection import TCPConnection
from .sockets.TCPSocket import TCPSocket, create_tcp_socket
import lib.server.logger as logger


ACCEPT_TIMEOUT_IN_SECONDS = 3

class Acceptor(threading.Thread):
    
    def __init__(self, host, port, fs_root, args):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.connections = {}
        self.fs_root = fs_root
        self.args = args
        self.socket = None
        self.should_run = True
        
    def run(self):
        logger.log_acceptor_starting(self.args)
        self.socket = create_tcp_socket()
        listen_address = (self.host, self.port)
        self.socket.bind(listen_address)
        self.socket.listen()

        logger.log_acceptor_listening(listen_address, self.args)
        self.socket.settimeout(ACCEPT_TIMEOUT_IN_SECONDS)
        try:
            while self.should_run:
                try:
                    client_socket, client_address = self.socket.accept()
                except timeout:
                    continue
                tcp_socket = TCPSocket(client_socket)
                self.connections[client_address] = TCPConnection(tcp_socket, self.fs_root, self.args)
                self.connections[client_address].start()
        except Exception as e:
            logger.log_error(e, self.args)
        

    def stop_running(self):
        self.socket.close()
        logger.log_acceptor_closed(self.args)
        for connection in self.connections:
            self.connections[connection].stop_running()
            self.connections[connection].join()
        self.should_run = False

        
