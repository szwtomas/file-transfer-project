import os
import socket
from socket import timeout
import time
from lib.client.constants import *
import lib.client.logger as logger

ROOT_FS_PATH = os.getcwd() + "/../client_fs_root/"

class UDPClient:
    '''This class is only used as parent class for SaWClient and GBNClient'''
    def get_request(self, path, operation):
        # Client First Message
        message = b""
        # packet sequence
        packet_seq = 0
        message += packet_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
        # operation
        message += operation.to_bytes(OPERATION_BYTES, byteorder="big")
        # path size
        message += len(path).to_bytes(PATH_SIZE_BYTES, byteorder="big")
        # path
        message += path.encode("UTF-8")
        # file size
        if operation == UPLOAD:
            message += os.path.getsize(ROOT_FS_PATH + path).to_bytes(FILE_SIZE_BYTES, byteorder="big")
        message += int(0).to_bytes(PACKET_SIZE - len(message), "big") # padding
        return message

    def make_request(self, server_ip, path, type, args):
        file_size = int(0).to_bytes(FILE_SIZE_BYTES, byteorder="big")
        start_timer = time.time()
        while time.time() - start_timer < MAX_WAITING_TIME:
            self.socket.sendto(self.get_request(path, type), (server_ip, SERVER_PORT))
            try:
                self.socket.settimeout(1)
                response, _ = self.socket.recvfrom(PACKET_SIZE)
                if not int.from_bytes(response[:PACKET_SEQUENCE_BYTES], "big") == 0:
                    start_timer = time.time()
                    continue
            except timeout:
                logger.log_server_not_responding_error(args)
                continue
            if type == DOWNLOAD and response[PACKET_SEQUENCE_BYTES] == 0:
                file_size = response[PACKET_SEQUENCE_BYTES + OPERATION_BYTES:PACKET_SEQUENCE_BYTES + 1 + FILE_SIZE_BYTES] #FIXME: ta bien esto? no

            return response[PACKET_SEQUENCE_BYTES], int.from_bytes(file_size, byteorder="big")
        return None, 0
    
    def parse_download_response(self, response):
        # Parse response packet and check if payload size is valid
        seq_num = int.from_bytes(response[:PACKET_SEQUENCE_BYTES], byteorder="big")
        payload_size = int.from_bytes(response[PACKET_SEQUENCE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES], byteorder="big")
        if payload_size > MAX_PAYLOAD_SIZE:
            return True, None, None
        payload = response[PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES + payload_size]
        return False, seq_num, payload
