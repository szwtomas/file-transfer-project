from socket import socket, AF_INET, SOCK_STREAM
from constants import LOCALHOST

class Server:

    def __init__(self, port):
        self.port = port

    def start(self):
        # start socket and return the received string as uppercase
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((LOCALHOST, self.port))
        s.listen(10)
        print("Server listening on port", self.port)
        while True:
            print("Waiting for connection...")
            try:
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.sendall(data.upper())
            except KeyboardInterrupt:
                print("Server stopped")
                break
            except Exception as e:
                print(e)

                        


        