from server.src.constants import CHUNK_SIZE
from utils import fs_utils

class FileSender:

    def send_file(self, socket, metadata):
        file_path = metadata.get_path()
        file_size = fs_utils.get_file_size(file_path)

        with open(file_path, "rb") as f:
            bytes_read = 0
            while bytes_read < file_size:
                bytes_to_read = min(file_size - bytes_read, CHUNK_SIZE)
                data = f.read(bytes_to_read)
                socket.send_data(data)
                bytes_read += bytes_to_read