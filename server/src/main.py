from server import TCPServer
from constants import PORT

if __name__ == "__main__":
    server = TCPServer(PORT)
    server.start()
