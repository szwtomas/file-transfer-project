import os
from .FileTransferValidator import FileTransferValidator
from sockets import TCPSocket
from metadata import Metadata
from constants import CHUNK_SIZE

class FileSender:

    def __init__(self, fs_root):
        self.fs_root = fs_root
        self.validator = FileTransferValidator()
        
    
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
        print("Starting is_download")
        file_path = os.path.join(self.fs_root, metadata.get_path())
        print(f"file_path: {file_path}")
        print("About to validate path:")
        self.validator.verify_valid_path(socket, file_path)
        print("Path validated")
        file_size = os.path.getsize(file_path)
        print(f"Filesize: {file_size}")
        self.validator.verify_valid_file_size(socket, file_size)
        print("Filesize validated")
        print("About to send ack message")
        self.send_ack_message(socket, file_size)
        try:
            offset = 0
            with open(file_path, "rb") as file:
                print(f"Sending file {file_path} to client")
                chunk_data = file.read(CHUNK_SIZE)
                print(f"Entering while loop, {chunk_data}, len: {len(chunk_data)}")
                while chunk_data:
                    message_bytes = self.build_payload_message(offset, chunk_data)
                    print(f"Sending message bytes: {message_bytes}")
                    socket.send_data(message_bytes)
                    print(f"Sent message bytes: {message_bytes}")
                    offset += len(chunk_data)
                    print(f"Offset: {offset}")
                    chunk_data = file.read(CHUNK_SIZE)
                    print(f"Chunk data: {chunk_data}")
                    

        except Exception as e:
            print(f"Error in send_file: {e}")


    def build_payload_message(self, offset: int, payload: bytes) -> bytes:
        print(f"Building payload message, offset: {offset}, payload: {payload}, len: {len(payload)}")
        data = b""
        data += offset.to_bytes(4, "big")
        data += len(payload).to_bytes(4, "big")
        data += payload
        return data


    def send_ack_message(self, socket, file_size: int):
        '''
        Sends an ack message to the client, with the following headers:
        1 byte: 0x0
        4 bytes: file size
        '''
        ack_message_btyes = b"\x00" + file_size.to_bytes(4, "big")
        print(f"Sending ack message: {ack_message_btyes}")
        socket.send_data(ack_message_btyes)
        print("Ack message sent")
        