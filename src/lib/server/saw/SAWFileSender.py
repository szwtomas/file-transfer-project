import os
from ..file_transfer.FileTransferValidator import FileTransferValidator

class SAWFileSender():
    
    def __init__(self, fs_root):
        self.fs_root = fs_root
        self.validator = FileTransferValidator()


    def send_file(self, socket, metadata, message_queue):
        file_path = os.path.join(self.fs_root, metadata.get_path())
        file_size = os.path.getsize(file_path)
        self.send_ack_message(socket, file_size)
        
    
    def send_ack_message(self, socket, file_size):
        data = b""
        data += "\x00"
        data += file_size.to_bytes(4, "big")
        socket.send_data(data)