from io import BufferedReader
from operator import ne
import os
from socket import timeout
import time

from ..constants import GBN_WINDOW_SIZE, MAX_PAYLOAD_SIZE, MAX_WAITING_TIME, PACKET_SEQUENCE_BYTES, PACKET_SIZE, PAYLOAD_SIZE_BYTES
from ..file_transfer.FileTransferValidator import FileTransferValidator
from .message_utils import build_ack_message, get_empty_bytes, send_message_until_acked
from ..constants import CHUNK_SIZE
from ..exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException

FIRST_MESSAGE_SEQUENCE_NUMBER = 1

class GBNFileSender:
    
    def __init__(self, fs_root, read_message, send_message):
        self.fs_root = fs_root
        self.validator = FileTransferValidator()
        self.read_message = read_message
        self.send_message = send_message


    def send_file(self, metadata):
        print("TAMO EN GBN Sending file")
        path = metadata.get_path()
        complete_path = f"{self.fs_root}/{path}"
        if not os.path.isfile(complete_path):
            ack_message = build_ack_message(0, True)
            self.send_message(ack_message)
            print("File does not exist")
            return
        file_size = os.path.getsize(complete_path)
        print(f"file size: {file_size}")
        ack = build_ack_message(file_size)
        self.send_message(ack)
        
        last_acked_recv = 1
        next_seq_to_send = 1
        print(f"About to send file: {path}")
        with open(complete_path, 'rb') as file:
            file.seek(0)
            expected_final_ack = file_size // MAX_PAYLOAD_SIZE + 2

            global_timer = time.time()
            while last_acked_recv < expected_final_ack:
                if  time.time() - global_timer > MAX_WAITING_TIME * 4:
                    print("timed out waiting for ack, exiting program")
                    #FIXME: logggg
                    return

                self.send_n_packets(last_acked_recv, GBN_WINDOW_SIZE, file)
                next_seq_to_send = last_acked_recv + GBN_WINDOW_SIZE

                last_ack_time = time.time()
                while time.time() - last_ack_time < 2:
                    try:
                        acknowledge = self.read_message()
                        recv_seq_num = int.from_bytes(acknowledge[:PACKET_SEQUENCE_BYTES], "big") # cut padding
                        if recv_seq_num <= last_acked_recv:
                            continue # ignore old acks
                        print(f"Received ack for packet {recv_seq_num}, last acked: {last_acked_recv}")
                        window_increment = recv_seq_num - last_acked_recv
                        last_acked_recv = recv_seq_num
                        last_ack_time = time.time()
                        global_timer = time.time()
                        if recv_seq_num == expected_final_ack:
                            break
                        self.send_n_packets(next_seq_to_send, window_increment, file)
                        next_seq_to_send = next_seq_to_send + window_increment
                    except timeout:
                        print("Server not responding")
                        continue
            print(f"File {path} sent successfully")
    

    def build_payload_message(self, seq_number: int, payload):
        data = b""
        data += seq_number.to_bytes(PACKET_SEQUENCE_BYTES, "big")
        data += len(payload).to_bytes(PAYLOAD_SIZE_BYTES, "big")
        data += payload
        remaining_bytes = PACKET_SIZE - len(data)
        if remaining_bytes > 0:
            data += get_empty_bytes(remaining_bytes)

        return data

    def send_n_packets(self, initial, n, file: BufferedReader):
        '''
        Sends n packets starting from initial sequence number 
        '''
        for seq_num in range(initial, initial + n):
            data = b''
            # sequence number
            data += seq_num.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
            file.seek((seq_num - 1) * MAX_PAYLOAD_SIZE)
            chunk = file.read(MAX_PAYLOAD_SIZE)
            if not chunk:
                break

            # chunk size
            data += len(chunk).to_bytes(PAYLOAD_SIZE_BYTES, byteorder="big")
            # chunk
            data += chunk
            data += int(0).to_bytes(PACKET_SIZE - len(data), "big") # padding
            print(f"Sending packet {seq_num}")
            self.send_message(data)
