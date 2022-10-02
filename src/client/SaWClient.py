from multiprocessing.reduction import ACKNOWLEDGE
import os
from socket import SOCK_DGRAM, socket, AF_INET
from constants import *
import time

class SaWClient:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start_download(self, server_ip, path):
        self.socket.connect((server_ip, SERVER_PORT))
        response, file_size = self.make_request(server_ip, path, DOWNLOAD)

        if response == 1:
            print("File not found")
            return

        with open(path, 'wb') as file:
            current_offset = 0
            while file_size > current_offset:
                try:
                    self.socket.settimeout(5)
                    response = self.socket.recvfrom(SAW_CHUNK_SIZE)
                    is_error, offset, payload = self.parse_download_response(response)
                except socket.timeout:
                    print("Server is not responding")
                    continue
                if is_error or offset != current_offset:
                    print("Error in received packet")
                    ack = current_offset.to_bytes(CHUNK_OFFSET_BYTES, byteorder="big")
                else:
                    ack = (current_offset + len(payload)).to_bytes(CHUNK_OFFSET_BYTES, byteorder="big")
                    current_offset += len(payload)
                    file.write(payload)

                self.socket.sendto(ack, (server_ip, SERVER_PORT))

    def start_upload(self, server_ip, path):
        self.socket.connect((server_ip, SERVER_PORT))
        response, _ = self.make_request(server_ip, path, UPLOAD)

        if response != 0: #error
            print("Error in upload response")
            return

        with open(path, 'rb') as file:
            file_size = os.path.getsize(path)
            current_offset = 0
            while file_size > current_offset:

                data = b''
                # offset
                data += current_offset.to_bytes(CHUNK_OFFSET_BYTES, byteorder="big")

                chunk = file.read(MAX_PAYLOAD_SIZE)
                # chunk size
                data += len(chunk).to_bytes(PAYLOAD_SIZE_BYTES, byteorder="big")
                # chunk
                data += chunk
                retry_count = 0
                while  retry_count <= RETRY_LIMIT: # wait until receive correct ack, retry RETRY_LIMIT times
                    self.socket.sendto(data, (server_ip, SERVER_PORT))
                    try:
                        self.socket.settimeout(5)
                        acknowledge = self.socket.recvfrom(CHUNK_OFFSET_BYTES)
                        if current_offset + len(chunk) == int.from_bytes(acknowledge, byteorder="big"):
                            break

                    except socket.timeout:
                        print("Server is not responding")
                        retry_count += 1
                        continue

                current_offset += MAX_PAYLOAD_SIZE

    def get_request(self, path, type):
        #Client First Message
        message = b""
        #operation
        message += bytes(type)
        #path size
        message += len(path).to_bytes(PATH_SIZE_BYTES, byteorder="big")
        #path
        message += path.encode("UTF-8")
        #file size
        if type == UPLOAD:
            message += os.path.getsize(path).to_bytes(FILE_SIZE_BYTES, byteorder="big")
        return message

    def make_request(self, server_ip, path, type):
        file_size = 0
        while True:
            self.socket.sendto(self.get_request(path, type), (server_ip, SERVER_PORT))
            try:
                self.socket.settimeout(1)
                response = self.socket.recvfrom(RESPONSE_STATUS_BYTES)
            except socket.timeout:
                print("Server is not responding")
                continue
            if type == DOWNLOAD and response == 0:
                try:
                    self.socket.settimeout(1)
                    file_size = self.socket.recvfrom(FILE_SIZE_BYTES)
                except socket.timeout:
                    print("Server is not responding")
                    continue
            return response, file_size

    def parse_download_response(self, response):
        # Parse response packet and check if payload size is valid
        offset = int.from_bytes(response[:CHUNK_OFFSET_BYTES], byteorder="big")
        payload_size = int.from_bytes(response[CHUNK_OFFSET_BYTES:CHUNK_OFFSET_BYTES + PAYLOAD_SIZE_BYTES], byteorder="big")
        if payload_size > MAX_PAYLOAD_SIZE:
            return True, None, None
        payload = response[CHUNK_OFFSET_BYTES + PAYLOAD_SIZE_BYTES:CHUNK_OFFSET_BYTES + PAYLOAD_SIZE_BYTES + payload_size]
        return False, offset, payload
