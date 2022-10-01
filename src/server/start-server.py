import os
from Server import Server
from constants import LOCALHOST, LISTEN_PORT

cwd = os.getcwd()
SERVER_FS_ROOT = os.getcwd() + "/../../fs_root"


def main():
    print(f"fs_root: {SERVER_FS_ROOT}")
    server = Server(LOCALHOST, LISTEN_PORT, SERVER_FS_ROOT)
    server.run()


if __name__ == "__main__":
    main()
