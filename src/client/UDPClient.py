import os
from socket import SOCK_DGRAM, socket, AF_INET
from constants import DOWNLOAD, FILE_SIZE_BYTES, PATH_SIZE_BYTES, RESPONSE_STATUS_BYTES, SERVER_PORT, CHUNK_SIZE_BYTES, CHUNK_OFFSET_BYTES, UPLOAD
from constants import CHUNK_SIZE
import time

class UDPClient:
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
                    offset = int.from_bytes(self.socket.recvfrom(CHUNK_OFFSET_BYTES), byteorder="big")
                    chunk_size = int.from_bytes(self.socket.recvfrom(CHUNK_SIZE_BYTES), byteorder="big")
                    chunk = self.socket.recvfrom(chunk_size)
                except:
                    print("Server is not responding")
                    continue
                if offset != current_offset:
                    print("Error in offset")
                    ack = current_offset.to_bytes(CHUNK_OFFSET_BYTES, byteorder="big")
                else:
                    ack = (current_offset + chunk_size).to_bytes(CHUNK_OFFSET_BYTES, byteorder="big")
                    current_offset += chunk_size
                    file.write(chunk)

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

                chunk = file.read(CHUNK_SIZE)
                # chunk size
                data += len(chunk).to_bytes(CHUNK_SIZE_BYTES, byteorder="big")
                # chunk
                data += chunk
                while True: # wait until receive correct ack
                    self.socket.sendto(data, (server_ip, SERVER_PORT))
                    try:
                        self.socket.settimeout(5)
                        response = self.socket.recvfrom(CHUNK_OFFSET_BYTES)
                        if current_offset + len(chunk) == int.from_bytes(response, byteorder="big"):
                            break

                    except socket.timeout:
                        print("Server is not responding")
                        continue

                current_offset += CHUNK_SIZE

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