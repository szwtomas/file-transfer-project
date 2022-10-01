import os
from Server import Server

HOST = "127.0.0.1"
PORT = 7878
cwd = os.getcwd()
SERVER_FS_ROOT = os.getcwd() + "../../fs_root"


def main():
    server = Server(HOST, PORT)
    server.run()


if __name__ == "__main__":
    main()
