import os

from ..constants import MAX_PAYLOAD_SIZE, PACKET_SEQUENCE_BYTES, PACKET_SIZE, PAYLOAD_SIZE_BYTES
from ..file_transfer.FileTransferValidator import FileTransferValidator
from .message_utils import build_ack_message, get_empty_bytes, send_message_until_acked
from ..constants import CHUNK_SIZE
from ..exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException
import lib.server.logger as logger

FIRST_MESSAGE_SEQUENCE_NUMBER = 1

class SAWFileSender:
    
    def __init__(self, fs_root, read_message, send_message, args):
        self.fs_root = fs_root
        self.validator = FileTransferValidator()
        self.read_message = read_message
        self.send_message = send_message
        self.args = args


    def send_file(self, metadata):
        file_path = os.path.join(self.fs_root, metadata.get_path())
        if not os.path.exists(file_path):
            ack_message = build_ack_message(0, True)
            self.send_message(ack_message)
            logger.log_file_not_found_error(metadata.get_path(), self.args)
            return
        logger.log_incoming_download_request(metadata.get_path(), self.args)
        file_size = os.path.getsize(file_path)
        ack_message = build_ack_message(file_size)
        self.send_message(ack_message)
        current_seq_number = 1
        operation_retries_count = 0
        max_operation_retries_count = 5
        try:
            with open(file_path, "rb") as file:
                chunk_data = file.read(MAX_PAYLOAD_SIZE)
                while chunk_data:
                    if operation_retries_count == max_operation_retries_count:
                        raise UDPMessageNotReceivedException("Max retries reached for first ACK")
                    message = self.build_payload_message(current_seq_number, chunk_data)
                    logger.log_send_pack_number(current_seq_number, self.args)
                    response = send_message_until_acked(self.read_message, self.send_message, current_seq_number, message)
                    if (not response) and current_seq_number == FIRST_MESSAGE_SEQUENCE_NUMBER:
                        ack_message = build_ack_message(file_size)
                        self.send_message(ack_message)
                        logger.log_send_pack_number(current_seq_number, self.args)
                        operation_retries_count += 1
                        continue
                    if not response:
                        # response = send_message_until_acked(self.read_message, self.send_message, current_seq_number, message)
                        continue
                    # if (int.from_bytes(response[:PACKET_SEQUENCE_BYTES], "big") - 1) == current_seq_number:
                    current_seq_number += 1
                    chunk_data = file.read(MAX_PAYLOAD_SIZE)

        except Exception as e:
            logger.log_error(e, self.args)
            return
        logger.log_download_success(metadata.get_path(), self.args)

    def build_payload_message(self, seq_number: int, payload):
        data = b""
        data += seq_number.to_bytes(PACKET_SEQUENCE_BYTES, "big")
        data += len(payload).to_bytes(PAYLOAD_SIZE_BYTES, "big")
        data += payload
        remaining_bytes = PACKET_SIZE - len(data)
        if remaining_bytes > 0:
            data += get_empty_bytes(remaining_bytes)

        return data

