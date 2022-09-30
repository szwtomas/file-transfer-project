from server.src.constants import CHUNK_SIZE
from utils import fs_utils

class FileSender:

    def send_file(self, socket, metadata):
        '''
        Sends the file to the client. The file is sent in chunks of size CHUNK_SIZE
        The headers are:
        4 bytes: Offset of the chunk
        4 bytes: size of the chunk
        '''
        data = b""
        file_path = metadata.get_path()
        file_size = fs_utils.get_file_size(file_path)

        with open(file_path, "rb") as f:
            bytes_read = 0
            while bytes_read < file_size:
                bytes_to_read = min(file_size - bytes_read, CHUNK_SIZE)
                data += bytes_read # Offset
                data += bytes_to_read # Size of the chunk
                data += f.read(bytes_to_read)
                socket.send_data(data)
                bytes_read += bytes_to_read