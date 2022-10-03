import os
from ..file_transfer.FileTransferValidator import FileTransferValidator
from .message_utils import send_message_until_acked
from ..constants import CHUNK_SIZE
from ..exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException

FIRST_MESSAGE_SEQUENCE_NUMBER = 1

class SAWFileSender:
    
    def __init__(self, fs_root, read_message, send_message):
        self.fs_root = fs_root
        self.validator = FileTransferValidator()
        self.read_message = read_message
        self.send_message = send_message


    def send_file(self, metadata):
        file_path = os.path.join(self.fs_root, metadata.get_path())
        file_size = os.path.getsize(file_path)
        ack_message = self.build_ack_message(file_size)
        self.send_message(ack_message)
        current_seq_number = 1
        operation_retries_count = 0
        max_operation_retries_count = 5
        try:
            with open(file_path, "rb") as file:
                print("Starting to send file")
                chunk_data = file.read(CHUNK_SIZE)
                while chunk_data:
                    if operation_retries_count == max_operation_retries_count:
                        raise UDPMessageNotReceivedException("Max retries reached for first ACK")
                    message = self.build_payload_message(current_seq_number, chunk_data)
                    response = send_message_until_acked(self.read_message, self.send_message, current_seq_number, message)
                    if not response and current_seq_number == FIRST_MESSAGE_SEQUENCE_NUMBER:
                        ack_message = self.build_ack_message(file_size)
                        self.send_message(ack_message)
                        operation_retries_count += 1
                        continue
                    current_seq_number += 1
                    chunk_data = file.read(CHUNK_SIZE)

        except UDPMessageNotReceivedException as e:
            print(f"Download FAILED: {e}")
        except Exception as e:
            print(f"Exception in SAWFileSender: {e}")


    def get_empty_bytes(self, amount):
            empty = 0
            return empty.to_bytes(amount, "big")


    def build_ack_message(self, file_size):
        data = b""
        seq_number = 0
        data += seq_number.to_bytes(4, "big")
        data += b"\x00"
        data += file_size.to_bytes(4, "big")
        data += self.get_empty_bytes(1024 - 4 - 1 - 4) # Clean programming masterclass
        return data


    def build_payload_message(self, seq_number, payload):
        data = b""
        data += seq_number.to_bytes(4, "big")
        data += len(payload).to_bytes(4, "big")
        data += payload
        remaining_bytes = CHUNK_SIZE - 8 - len(payload)
        if remaining_bytes > 0:
            data += self.get_empty_bytes(remaining_bytes)

        return data

