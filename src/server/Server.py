from Acceptor import Acceptor
from user_commands import QUIT, QUIT_ABREVIATED

class Server:

    def __init__(self, host, port, fs_root):
        self.acceptor = None
        self.host = host
        self.port = port
        self.fs_root = fs_root

    def run(self):
        print("Running server...")
            
        # We can optionally accept host and port as command line parameters in the future
        self.acceptor = Acceptor(self.host, self.port, self.fs_root)
        self.acceptor.start()
        while True:
            user_command = input()
            if user_command == QUIT or user_command == QUIT_ABREVIATED:
                print("Server stopping")
                self.acceptor.stop_running()
                self.acceptor.join()
                break
            elif user_command == "hello" or user_command == "h":
                print("Hello :)")
            elif user_command == "write":
                print("Trying to write file in fs_root: ")
                f = open(FS_ROOT + "/hello.txt", "w")
                f.write("Hello world")
                f.close()
            else:
                print("Unknown command :(")

