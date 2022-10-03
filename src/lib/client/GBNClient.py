from multiprocessing.reduction import ACKNOWLEDGE
import os
from socket import SOCK_DGRAM, socket, AF_INET
from constants import *
import time
import logger

class GBNClient:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start_download(self, server_ip, path, port, args):
        self.socket.connect((server_ip, SERVER_PORT))
        response, file_size = self.make_request(server_ip, path, DOWNLOAD)

        if response == 1:
            print("File not found")
            return

        last_ack = time.time()
        with open(path, 'wb') as file:
            current_seq = 1
            while file_size > (current_seq - 1) * MAX_PAYLOAD_SIZE:
                if time.time() - last_ack > MAX_WAITING_TIME:
                    print("ADD LOGGER ERROR: SERVER TIMEOUT")
                    return
                try:
                    self.socket.settimeout(5)
                    response, _ = self.socket.recvfrom(PACKET_SIZE)
                    last_ack = time.time()
                    is_error, seq_num, payload = self.parse_download_response(response)
                except socket.timeout:
                    print("Server is not responding")
                    continue
                if is_error or seq_num != current_seq:
                    print("Error in received packet")
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                else:
                    ack = seq_num.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                    current_seq += 1
                    file.write(payload)
                    
                ack += int(0).to_bytes(PACKET_SIZE - len(ack), "big") # padding
                self.socket.sendto(ack, (server_ip, SERVER_PORT))

    def start_upload(self, server_ip, path, port, args):
        self.socket.connect((server_ip, port))
        response, _ = self.make_request(server_ip, path, UPLOAD)

        if response == 1: #error
            print("Error in upload response")
            return

        current_seq = 1
        with open(path, 'rb') as file:
            file.seek(0)
            file_size = os.path.getsize(path)
            current_offset = 0
            while file_size > current_offset:
                chunks_sent = 0
                file.seek(current_offset)
                for _ in range(GBN_WINDOW_SIZE): # FIXME: we should decide if we want to send one mor packet for each ack received or if we want to send all the packets and wait for all the acks
                    data = b''
                    # sewuence number
                    data += current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")

                    chunk = file.read(MAX_PAYLOAD_SIZE)
                    if not chunk:
                        break

                    # chunk size
                    data += len(chunk).to_bytes(PAYLOAD_SIZE_BYTES, byteorder="big")
                    # chunk
                    data += chunk
                    data += int(0).to_bytes(PACKET_SIZE - len(data), "big") # padding
                    self.socket.sendto(data, (server_ip, SERVER_PORT))
                    chunks_sent += 1

                last_ack = time.time()
                for _ in range(chunks_sent):
                    try:
                        while True:
                            if time.time() - last_ack < MAX_WAITING_TIME:
                                print("ADD LOGGER ERROR: SERVER TIMEOUT")
                                return
                            self.socket.settimeout(3)
                            acknowledge, _ = self.socket.recvfrom(PACKET_SIZE)
                            acknowledge = acknowledge[:PACKET_SEQUENCE_BYTES] # cut padding
                            last_ack = time.time()
                            if acknowledge >= current_seq:
                                break

                    except socket.timeout:
                        print("Server is not responding")
                        continue
                    
                    if acknowledge > current_seq:
                        current_seq += 1
                        current_offset += MAX_PAYLOAD_SIZE
                
    def get_request(self, path, type):
        # Client First Message
        message = b""
        # packet sequence
        packet_seq = 0
        message += packet_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
        # operation
        message += bytes(type)
        # path size
        message += len(path).to_bytes(PATH_SIZE_BYTES, byteorder="big")
        # path
        message += path.encode("UTF-8")
        # file size
        if type == UPLOAD:
            message += os.path.getsize(path).to_bytes(FILE_SIZE_BYTES, byteorder="big")
        message += int(0).to_bytes(PACKET_SIZE - len(message), "big") # padding
        return message

    def make_request(self, server_ip, path, type):
        file_size = 0
        start_timer = time.time()
        while time.time() - start_timer < MAX_WAITING_TIME:
            self.socket.sendto(self.get_request(path, type), (server_ip, SERVER_PORT))
            try:
                self.socket.settimeout(1)
                response, _ = self.socket.recvfrom(PACKET_SIZE)
                if not int.from_bytes(response[:PACKET_SEQUENCE_BYTES]) == 0:
                    start_timer = time.time()
                    continue
            except socket.timeout:
                print("Server is not responding")
                continue
            if type == DOWNLOAD and response[PACKET_SEQUENCE_BYTES] == 0:
                file_size = response[PACKET_SEQUENCE_BYTES:PACKET_SEQUENCE_BYTES + FILE_SIZE_BYTES] #FIXME: ta bien esto?

            return response[PACKET_SEQUENCE_BYTES], file_size
        return None, 0  # add to logger that program timeouted

    def parse_download_response(self, response):
        # Parse response packet and check if payload size is valid
        seq_num = int.from_bytes(response[:PACKET_SEQUENCE_BYTES], byteorder="big")
        payload_size = int.from_bytes(response[PACKET_SEQUENCE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES], byteorder="big")
        if payload_size > MAX_PAYLOAD_SIZE:
            return True, None, None
        payload = response[PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES + payload_size]
        return False, seq_num, payload
