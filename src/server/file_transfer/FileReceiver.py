from sockets import TCPSocket
from constants import CHUNK_SIZE
from metadata import Metadata
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
        self.validator.verify_valid_file_size(socket, metadata.get_file_size())
        self.send_ack_message(socket)

        path = f"{self.fs_root}/{metadata.get_path()}"
        print("PATH: {path}")
        file_size = metadata.get_file_size()

        try:
            with open(path, "wb") as file:
                print(f"About to receive file: {path}")
                while file_size > 0:
                    _ = int.from_bytes(socket.read_data(4), byteorder="big") # we don't need the offset in TCP
                    chunk_size = int.from_bytes(socket.read_data(4), byteorder="big")
                    chunk = socket.read_data(chunk_size)
                    print(f"Received chunk: {chunk}")
                    file.write(chunk)
                    file_size -= CHUNK_SIZE

        except Exception as e:
            print(f"Exception receiving file: {e}")

    
    def send_ack_message(self, socket):
        ack_message_btyes = b"\x00"
        print(f"Sending ack message: {ack_message_btyes}")
        socket.send_data(ack_message_btyes)

    