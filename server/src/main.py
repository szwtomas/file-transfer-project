from server import Server
from constants import PORT

if __name__ == "__main__":
    server = Server(PORT)
    server.start()
