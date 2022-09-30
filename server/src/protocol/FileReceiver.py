from utils import fs_utils
class FileUploader():

    def receive_file(socket, metadata):
        '''
        Receives the file from the client, and saves it to the server.
        The headers are:
        4 bytes: Offset of the chunk
        4 bytes: size of the chunk
        '''
        data = b""
        file_path = metadata.get_path()
        file_size = metadata.get_file_size()

        with open(file_path, "wb") as f: # overwrite the file if it exists
            bytes_read = 0
            while bytes_read < file_size:
                offset = socket.read_data(4) # FIXME: should we use it?
                bytes_to_read = socket.read_data(4)
                data = socket.read_data(bytes_to_read)
                f.write(data)
