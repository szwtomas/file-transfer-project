import os
from ..exceptions.InvalidPathException import InvalidPathException
from ..exceptions.FileSizeNotSupportedException import FileSizeNotSupportedException
from ..file_transfer.utils import is_valid_path_syntax
from ..constants import MAX_FILE_SIZE_SUPPORTED_IN_BYTES, ERROR_BYTES, CHUNK_SIZE


class SAWFileReceiver:

    def __init__(self, fs_root, read_message, send_message):
        self.fs_root = fs_root
        self.read_message = read_message
        self.send_message = send_message


    def receive_file(self, metadata):
        path = f"{self.fs_root}/{metadata.get_path()}"
        self.verify_path(path)
        file_size = metadata.get_file_size()
        self.verify_file_size(file_size)
        try:
            with open(path, "wb") as file:
                pass

        except Exception as e:
            print(f"Exception receiving file: {e}")
        


    def verify_file_size(self, file_size):
        if file_size > MAX_FILE_SIZE_SUPPORTED_IN_BYTES:
            self.send_message(self.get_invalid_operation_message())
            raise FileSizeNotSupportedException(f"SAW File receiver: File size not supported: {file_size}")

    
    def verify_path(self, path):
        if not os.path.isfile(path) or not is_valid_path_syntax(path):
            self.send_message(self.get_invalid_operation_message())
            raise InvalidPathException(f"SAW File Receiver, invalid path: {path}")
        

    def get_invalid_operation_message(self):
        seq_number = 0 
        data = b"" + seq_number.to_bytes(4, "big") + ERROR_BYTES
        return data

