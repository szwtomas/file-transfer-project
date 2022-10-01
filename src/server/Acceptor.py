import threading
from socket import AF_INET, SOCK_STREAM, socket, timeout
from TCPConnection import TCPConnection
from sockets.TCPSocket import TCPSocket

ACCEPT_TIMEOUT_IN_SECONDS = 10

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
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        self.socket.settimeout(ACCEPT_TIMEOUT_IN_SECONDS)
        try:
            while self.should_run:
                client_socket, client_address = self.socket.accept()
                tcp_socket = TCPSocket(client_socket)
                self.connections[client_address] = TCPConnection(tcp_socket, self.fs_root)
                self.connections[client_address].handle_connection()
        except timeout:
            # TODO: Add timeout error handling
            # Probably close connections and that sort of thing
            print("Timeout")
        except Exception as e:
            print(f"Error: {e}")
        

    def stop_running(self):
        self.socket.close()
        for connection in self.connections:
            self.connections[connection].stop_running()
            self.connections[connection].join()
        self.should_run = False

        
