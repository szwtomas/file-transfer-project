from stat import FILE_ATTRIBUTE_ARCHIVE
from protocol.MetadataParser import MetadataParser
from protocol.FileSender import FileSender
from protocol.FileReceiver import FileReceiver
from server.src.constants import CHUNK_MESSAGE_SIZE_BYTES, CHUNK_SIZE, FILE_SIZE_BYTES
import utils.fs_utils as fs_utils

class Server:

    def __init__(self, port):
        self.port = port
        self.metadata_parser = MetadataParser()
        self.file_sender = FileSender()
        self.file_receiver = FileReceiver()

    # TODO: Implement concurrently with a threadpool or something
    def start(self):
        '''
        Starts the server, listents indefinitely for connections and handles
        the requests. 
        '''
        while True:
            socket = self.get_connection()
            data = socket.read_data()
            try:
                metadata = self.metadata_parser.parse(data)
            except Exception as e:
                print(str(e))
                continue

            self.send_headers_to_client(socket, metadata)

            if metadata.is_download():    
                self.send_file_to_client(socket, metadata)
            else:
                self.receive_file_from_client(socket, metadata)


    def send_file_to_client(self, socket, metadata): 
        self.file_sender.send_file(socket, metadata)

    def receive_file_from_client(self, socket, metadata):
        self.file_receiver.receive_file(socket, metadata)

    def send_headers_to_client(self, socket, metadata):
        if metadata.is_download():
            headers_data = self.get_download_response_bytes(socket, metadata)
        else:
            headers_data = b""
            pass #Implement for upload


        socket.send_data(headers_data)

    def get_download_response_bytes(self, socket, metadata):
        data = b""
        # 0 means OK. 1 means error
        data += bytes(0) if fs_utils.path_exists(metadata.get_path()) else bytes(1)

        file_path = metadata.get_path()
        file_size = fs_utils.get_file_size(file_path)
                
        data += file_size.to_bytes(FILE_SIZE_BYTES, byteorder="big")

        data += CHUNK_SIZE.to_bytes(CHUNK_MESSAGE_SIZE_BYTES, byteorder="big")

        return data
