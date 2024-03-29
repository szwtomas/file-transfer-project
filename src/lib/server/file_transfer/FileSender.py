import os
from .FileTransferValidator import FileTransferValidator
from ..sockets.TCPSocket import TCPSocket
from ..metadata.Metadata import Metadata
from ..constants import CHUNK_SIZE, FILE_SIZE_BYTES, MAX_PAYLOAD_SIZE, PACKET_SEQUENCE_BYTES, PACKET_SIZE, PAYLOAD_SIZE_BYTES
import lib.server.logger as logger

class FileSender:

    def __init__(self, fs_root, args):
        self.fs_root = fs_root
        self.validator = FileTransferValidator()
        self.args = args
        
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
        file_path = os.path.join(self.fs_root, metadata.get_path())
        self.validator.verify_valid_path(socket, file_path)
        file_size = os.path.getsize(file_path)
        logger.log_incoming_download_request(file_path, self.args)
        self.validator.verify_valid_file_size(socket, file_size)
        self.send_ack_message(socket, file_size)
        try:
            seq_number = 0
            with open(file_path, "rb") as file:
                chunk_data = file.read(MAX_PAYLOAD_SIZE)
                while chunk_data:
                    message_bytes = self.build_payload_message(seq_number, chunk_data)
                    socket.send_data(message_bytes)
                    seq_number += 1
                    logger.log_send_pack_number(seq_number, self.args)
                    chunk_data = file.read(MAX_PAYLOAD_SIZE)

        except Exception as e:
            logger.log_error(e)

    def build_payload_message(self, sequence_number: int, payload: bytes) -> bytes:
        data = b""
        data += sequence_number.to_bytes(PACKET_SEQUENCE_BYTES, "big")
        payload_len_bytes = len(payload).to_bytes(PAYLOAD_SIZE_BYTES, "big")
        data += payload_len_bytes
        data += payload
        remaining_bytes = PACKET_SIZE - len(data)
        if remaining_bytes > 0:
            data += self.get_empty_bytes(remaining_bytes)
        return data

    def get_empty_bytes(self, amount):
        empty = 0
        return empty.to_bytes(amount, "big")


    def get_ack_message(self, file_size: int) -> bytes:
        seq_number = 0
        return seq_number.to_bytes(PACKET_SEQUENCE_BYTES, "big") + b"\x00" + file_size.to_bytes(FILE_SIZE_BYTES, "big") + self.get_empty_bytes(CHUNK_SIZE - PACKET_SEQUENCE_BYTES - FILE_SIZE_BYTES - 1)

    def send_ack_message(self, socket, file_size: int):
        '''
        Sends an ack message to the client, with the following headers:
        1 byte: 0x0
        4 bytes: file size
        Rest of bytes filled with 0 (Total of 4096 bytes)
        '''
        ack_message_btyes = self.get_ack_message(file_size)
        socket.send_data(ack_message_btyes)
        