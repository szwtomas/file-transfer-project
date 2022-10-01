import threading
from metadata.MetadataParser import MetadataParser
from file_transfer import FileSender, FileReceiver

class TCPConnection(threading.Thread):
    
    def __init__(self, socket, fs_root):
        threading.Thread.__init__(self)
        self.socket = socket
        self.fs_root = fs_root
        self.metadata_parser = MetadataParser()
        self.file_sender = FileSender()
        self.file_receiver = FileReceiver()
        

    def handle_connection(self):
        try:
            data = self.socket.read_data()
            metadata = self.metadata_parser.parse(data)
            self.transfer_file(metadata)
        except Exception as e:
            # TODO: Add error handling
            print(f"Error: {e}")


    def transfer_file(self, metadata):
        try:
            if metadata.is_download:
                self.file_sender.send_file(self.socket, self.fs_root, metadata.path)
            else:
                self.file_receiver.receive_file(self.socket, self.fs_root, metadata.path, metadata.file_size)
        except Exception as e:
            print(f"Exception: {e}")

    
    def stop_running(self):
        self.socket.close()