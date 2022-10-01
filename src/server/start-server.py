import os
from Server import Server
from constants import LOCALHOST, LISTEN_PORT

SERVER_FS_ROOT = os.getcwd() + "/../../fs_root"

def main():
    # We can optionally accept host and port as command line parameters in the future
    server = Server(LOCALHOST, LISTEN_PORT, SERVER_FS_ROOT)
    server.run()


if __name__ == "__main__":
    main()
