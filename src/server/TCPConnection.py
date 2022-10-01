import threading
from metadata.MetadataParser import MetadataParser
from file_transfer.FileReceiver import FileReceiver
from file_transfer.FileSender import FileSender

class TCPConnection(threading.Thread):
    
    def __init__(self, socket, fs_root):
        threading.Thread.__init__(self)
        self.socket = socket
        self.fs_root = fs_root
        self.metadata_parser = MetadataParser()
        self.file_sender = FileSender(fs_root)
        self.file_receiver = FileReceiver()
        

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
        try:
            if metadata.get_is_download():
                self.file_sender.send_file(self.socket, metadata)
            else:
                self.file_receiver.receive_file(self.socket, self.fs_root, metadata, metadata.file_size)
        except Exception as e:
            print(f"Exception in transfer_file: {e}")


    
    def stop_running(self):
        self.socket.close()