import os
from exceptions import FileDoesNotExistException, FileSizeNotSupportedException
from sockets import TCPSocket
from metadata import Metadata
from constants import CHUNK_SIZE, MAX_FILE_SIZE_SUPPORTED_IN_BYTES 

class FileSender:

    def send_file(self, socket: TCPSocket, metadata: Metadata):
        '''
        Sends file to client
        It first sends an ack message with operation confirmation, or 
        a message indicating the request is invalid.
        If the download is confirmed, then it will start sending messages
        with the following format:

        - 4 bytes: Offset of the chunk in bytes
        - 4 bytes: Payload size in bytes
        - payload
        '''
        file_path = os.path.join(self.fs_root, metadata.path)
        self.verify_valid_path(socket, file_path)        
        file_size = os.path.getsize(file_path)
        self.verify_valid_file_size(socket, file_size)
        
        try:
            offset = 0
            with open(file_path, "rb") as file:
                chunk_data = file.read(CHUNK_SIZE)
                while chunk_data is not None:
                    message_bytes = self.build_payload_message(offset, chunk_data)
                    socket.send_data(message_bytes)
                    offset += len(chunk_data)
                    chunk_data = file.read(CHUNK_SIZE)

        except Exception as e:
            print(f"Error: {e}")


    def build_payload_message(self, offset: int, payload: bytes) -> bytes:
        data = b""
        data += offset.to_bytes(4, "big")
        data += len(payload).to_bytes(4, "big")
        data += payload
        return data


    def send_ack_message(socket, file_size: int):
        '''
        Sends an ack message to the client, with the following headers:
        1 byte: 0x0
        4 bytes: file size
        '''
        ack_message_btyes = b"\x00" + file_size.to_bytes(4, "big")
        socket.send_data(ack_message_btyes)
        

    def send_invalid_download_message(socket: TCPSocket):
        message_bytes = b"\x01"
        socket.send_data(message_bytes)

    def verify_valid_path(self, socket: TCPSocket, file_path: str):
        if not os.path.isfile(file_path):
            error_message = f"File {file_path} does not exist"
            self.send_invalid_download_message(socket)
            raise FileDoesNotExistException(error_message)
    
    def verify_file_size(self, socket: TCPSocket, file_size: int):
        if file_size > MAX_FILE_SIZE_SUPPORTED_IN_BYTES:
            self.send_invalid_download_message(socket)
            error_message = f"File size {file_size} is not supported, max file size is {MAX_FILE_SIZE_SUPPORTED_IN_BYTES}"
            raise FileSizeNotSupportedException(error_message)