from .Acceptor import Acceptor
from .user_commands import QUIT, QUIT_ABREVIATED
import lib.server.logger as logger

class TCPServer:

    def __init__(self, host, port, fs_root, args):
        self.acceptor = None
        self.host = host
        self.port = port
        self.fs_root = fs_root
        self.args = args


    def run(self):
        self.acceptor = Acceptor(self.host, self.port, self.fs_root, self.args)
        self.acceptor.start()
        while True:
            user_command = input()
            if user_command == QUIT or user_command == QUIT_ABREVIATED:
                self.acceptor.stop_running()
                self.acceptor.join()
                break
            elif user_command == "hello" or user_command == "h":
                print("Hello :)")
            else:
                print("Unknown command :(")

        logger.log_server_stop()