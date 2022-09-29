from curses import meta
import os
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

            self.send_response_to_client(socket, metadata)

            if metadata.is_download():    
                self.send_file_to_client(socket, metadata)
            else:
                self.receive_file_from_client(socket, metadata)


    def send_file_to_client(self, socket, metadata): 
        self.file_sender.send_file(socket, metadata)

    def receive_file_from_client(self, socket, metadata):
        self.file_receiver.receive_file(socket, metadata)

    def send_response_to_client(self, socket, metadata):
        if metadata.is_download():
            data = self.get_download_response_bytes(socket, metadata)
        else:
            data = b""
            data = self.get_upload_response_bytes(socket, metadata)

        socket.send_data(data)

    def get_download_response_bytes(self, socket, metadata):
        data = b""
        # 0 means OK. 1 means error
        data += bytes(0) if fs_utils.path_exists(metadata.get_path()) else bytes(1)
        # TODO: if error, should we return here?

        file_path = metadata.get_path()
        file_size = fs_utils.get_file_size(file_path)
                
        data += file_size.to_bytes(FILE_SIZE_BYTES, byteorder="big")

        data += CHUNK_SIZE.to_bytes(CHUNK_MESSAGE_SIZE_BYTES, byteorder="big")

        with open(fs_utils.get_full_path(file_path), "rb") as f:
            while file_size > 0:
                msg_size = min(CHUNK_SIZE, file_size)
                chunk_data = f.read(msg_size)
                data += chunk_data
                file_size -= len(chunk_data)
        return data

    def get_upload_response_bytes(self, socket, metadata):
        data = b""
        # 0 means OK. 1 means error
        data += bytes(0) if self.check_space_available(metadata.get_file_size()) else bytes(1)
        return data

    # FIXME: do we need this?
    def check_space_available(self, file_size):
        '''
        Returns true if there is enough space available to store the file.
        '''
        #shutil.disk_usage(path) may be useful to check the available space
        return True

