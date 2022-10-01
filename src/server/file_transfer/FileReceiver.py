from server.sockets.TCPSocket import TCPSocket
from constants import CHUNK_SIZE
from metadata import Metadata
from FileTransferValidator import FileTransferValidator

class FileReceiver:

    def __init__(self, fs_root):
        self.fs_root = fs_root
        self.validator = FileTransferValidator()

    def receive_file(self, socket: TCPSocket, metadata: Metadata):
        '''
        Receives file from the client
        It first respondes an ack (0) or an error message, it's a 1 byte message
        After that, it starts receiving messages with this format:
        - 4 bytes: Offset of the chunk
        - 4 bytes: size of the chunk
        - chunk_size bytes: payload 
        '''
        self.validator.verify_valid_file_size(socket, metadata.get_file_size())

    