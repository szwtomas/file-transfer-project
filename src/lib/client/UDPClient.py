import os
import socket
import time
from lib.client.constants import *
#from constants import DOWNLOAD, FILE_SIZE_BYTES, MAX_PAYLOAD_SIZE, MAX_WAITING_TIME, PACKET_SEQUENCE_BYTES, PACKET_SIZE, PATH_SIZE_BYTES, PAYLOAD_SIZE_BYTES, SERVER_PORT, UPLOAD


class UDPClient:
    '''This class is only used as parent class for SaWClient and GBNClient'''
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
        return None, 0  # FIXME: add to logger that program timeouted
    
    def parse_download_response(self, response):
        # Parse response packet and check if payload size is valid
        seq_num = int.from_bytes(response[:PACKET_SEQUENCE_BYTES], byteorder="big")
        payload_size = int.from_bytes(response[PACKET_SEQUENCE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES], byteorder="big")
        if payload_size > MAX_PAYLOAD_SIZE:
            return True, None, None
        payload = response[PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES + payload_size]
        return False, seq_num, payload
