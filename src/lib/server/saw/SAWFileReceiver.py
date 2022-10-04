import os
from lib.server.saw.message_utils import build_ack_message
from ..exceptions.InvalidPathException import InvalidPathException
from ..exceptions.FileSizeNotSupportedException import FileSizeNotSupportedException
from ..constants import MAX_FILE_SIZE_SUPPORTED_IN_BYTES, ERROR_BYTES, PACKET_SIZE, PACKET_SEQUENCE_BYTES


class SAWFileReceiver:
    def __init__(self, fs_root, read_message, send_message):
        self.fs_root = fs_root
        self.read_message = read_message
        self.send_message = send_message

    def receive_file(self, metadata):
        path = self.get_path()
        file_size = metadata.get_file_size()
        print('verify file size')
        self.verify_file_size(file_size)
        ack = build_ack_message(file_size)
        self.send_message(ack)
        current_seq = 1
        try:
            with open(path, "wb") as file:
                print(f"About to receive file: {path}")
                while file_size > 0:
                    packet = self.read_message()
                    print(f"PACKET {packet[:16]}")
                    seq_number = int.from_bytes(packet[:PACKET_SEQUENCE_BYTES], byteorder="big")
                    if seq_number == 0:
                        ack = build_ack_message(file_size)
                        self.send_message(ack)
                        continue

                    if seq_number != current_seq:
                        ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, "big")
                    else:
                        current_seq += 1
                        ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, "big")
                        chunk_size = int.from_bytes(packet[PACKET_SEQUENCE_BYTES:PACKET_SEQUENCE_BYTES + 4], byteorder="big")
                        chunk = packet[PACKET_SEQUENCE_BYTES + 4:PACKET_SEQUENCE_BYTES + 4 + chunk_size]
                        file.write(chunk)
                        file_size -= chunk_size
                    ack += int(0).to_bytes(PACKET_SIZE - len(ack), "big")
                    self.send_message(ack)

        except Exception as e:
            print(f"Exception receiving file: {e}")

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
        data += b"\x00" * (PACKET_SIZE - len(data)) # Fills remaining bytes with 0
        return data

    
    def get_path(self, metadata):
        file_path = metadata.get_path()
        return f"{self.fs_root}/{file_path}"

