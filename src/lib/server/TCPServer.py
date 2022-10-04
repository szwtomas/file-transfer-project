from .Acceptor import Acceptor
from .user_commands import QUIT, QUIT_ABREVIATED

class TCPServer:

    def __init__(self, host, port, fs_root):
        self.acceptor = None
        self.host = host
        self.port = port
        self.fs_root = fs_root

    def run(self):
        print("Running server...")
        self.acceptor = Acceptor(self.host, self.port, self.fs_root)
        self.acceptor.start()
        while True:
            user_command = input()
            if user_command == QUIT or user_command == QUIT_ABREVIATED:
                print("Server stopping")
                self.acceptor.stop_running()
                print("About to join acceptor thread")
                self.acceptor.join()
                print("Acceptor thread joined")
                break
            elif user_command == "hello" or user_command == "h":
                print("Hello :)")
            else:
                print("Unknown command :(")

        print("Server stoped")