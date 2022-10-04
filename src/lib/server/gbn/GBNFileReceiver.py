import os
from re import A

from lib.server.saw.message_utils import build_ack_message
from ..exceptions.InvalidPathException import InvalidPathException
from ..exceptions.FileSizeNotSupportedException import FileSizeNotSupportedException
from ..constants import MAX_FILE_SIZE_SUPPORTED_IN_BYTES, ERROR_BYTES, PACKET_SIZE, PACKET_SEQUENCE_BYTES, PAYLOAD_SIZE_BYTES
import lib.server.logger as logger


class GBNFileReceiver:
    def __init__(self, fs_root, read_message, send_message, args):
        self.fs_root = fs_root
        self.read_message = read_message
        self.send_message = send_message
        self.args = args

    def receive_file(self, metadata):
        path = f"{self.fs_root}/{metadata.get_path()}"
        file_size = metadata.get_file_size()
        logger.log_incoming_upload_request(metadata.get_path(), self.args)
        self.verify_file_size(file_size)
        ack = build_ack_message(file_size)
        self.send_message(ack)
        current_seq = 1
        try:
            with open(path, "wb") as file:
                while file_size > 0:
                    packet = self.read_message()
                    seq_number = int.from_bytes(packet[:PACKET_SEQUENCE_BYTES], byteorder="big")
                    logger.log_packet_seq_number(seq_number, self.args)
                    if seq_number == 0:
                        ack = build_ack_message(file_size)
                        self.send_message(ack)
                        continue
                    # chequear que el seguence number sea el esperado
                    elif seq_number > current_seq:
                        ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                    elif seq_number < current_seq:
                        continue
                    else:
                        current_seq += 1
                        ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, "big")
                        chunk_size = int.from_bytes(packet[PACKET_SEQUENCE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES], byteorder="big")
                        chunk = packet[PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES + chunk_size]
                        file.write(chunk)
                        file_size -= chunk_size
                    ack += int(0).to_bytes(PACKET_SIZE - len(ack), "big")
                    self.send_message(ack)
            logger.log_upload_success(metadata.get_path(), self.args)

        except Exception as e:
            logger.log_error(e, self.args)


    def verify_file_size(self, file_size):
        if file_size > MAX_FILE_SIZE_SUPPORTED_IN_BYTES:
            self.send_message(self.get_invalid_operation_message())
            raise FileSizeNotSupportedException(f"SAW File receiver: File size not supported: {file_size}")

    
    def verify_path(self, path):
        if not os.path.isfile(path):
            self.send_message(self.get_invalid_operation_message())
            raise InvalidPathException(f"SAW File Receiver, invalid path: {path}")
        

    def get_invalid_operation_message(self):
        seq_number = 0 
        data = b"" + seq_number.to_bytes(PACKET_SEQUENCE_BYTES, "big") + ERROR_BYTES
        # padding
        data += b"\x00" * (PACKET_SIZE - len(data))
        return data

