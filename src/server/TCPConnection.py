import threading
from metadata.MetadataParser import MetadataParser
from file_transfer.FileReceiver import FileReceiver
from file_transfer.FileSender import FileSender
from sockets import TCPSocket

class TCPConnection(threading.Thread):
    
    def __init__(self, socket: TCPSocket, fs_root):
        threading.Thread.__init__(self)
        self.socket = socket
        self.fs_root = fs_root
        self.metadata_parser = MetadataParser()
        self.file_sender = FileSender(fs_root)
        self.file_receiver = FileReceiver(fs_root)
        

    def run(self):
        self.handle_connection()


    def handle_connection(self):
        try:
            data = self.socket.read_data()
            metadata = self.metadata_parser.parse(data)
            self.transfer_file(metadata)
        except Exception as e:
            # TODO: Add error handling
            print(f"Error in handle_connection: {e}  ")


    def transfer_file(self, metadata):
        print("Calling transfer_file")
        try:
            if metadata.get_is_download():
                print("is_download")
                self.file_sender.send_file(self.socket, metadata)
            else:
                print("is_download")
                self.file_receiver.receive_file(self.socket, metadata)
        except Exception as e:
            print(f"Exception in transfer_file: {e}")


    
    def stop_running(self):
        self.socket.close()