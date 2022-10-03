from lib.client.constants import PAYLOAD_SIZE_BYTES
from lib.server.metadata.MetadataParser import SEQ_NUMBER_BYTES
from ..sockets.TCPSocket import TCPSocket
from ..constants import CHUNK_SIZE
from ..metadata.Metadata import Metadata
from .FileTransferValidator import FileTransferValidator

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
    
        self.validator.validate_path_syntax(socket, metadata.get_path())
        self.validator.verify_valid_file_size(socket, metadata.get_file_size())
        self.send_ack_message(socket)

        path = f"{self.fs_root}/{metadata.get_path()}"
        print(f"PATH: {path}")
        file_size = metadata.get_file_size()

        try:
            with open(path, "wb") as file:
                print(f"About to receive file: {path}")
                while file_size > 0:
                    _ = int.from_bytes(socket.read_data(SEQ_NUMBER_BYTES), byteorder="big")
                    chunk_size = int.from_bytes(socket.read_data(PAYLOAD_SIZE_BYTES), byteorder="big")
                    chunk = socket.read_data(chunk_size)
                    file.write(chunk)
                    file_size -= chunk_size

        except Exception as e:
            print(f"Exception receiving file: {e}")

    def get_empty_bytes(self, amount):
        empty = 0
        return empty.to_bytes(amount, "big")

    def send_ack_message(self, socket):
        # we assume there is enough space to receive the file
        ack_message_btyes = self.get_empty_bytes(1024)
        socket.send_data(ack_message_btyes)
        print(f"Ack message sent")
