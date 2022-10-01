import os
from socket import SOCK_DGRAM, socket, AF_INET
from constants import DOWNLOAD, FILE_SIZE_BYTES, PATH_SIZE_BYTES, RESPONSE_STATUS_BYTES, SERVER_PORT, CHUNK_SIZE_BYTES, CHUNK_OFFSET_BYTES, UPLOAD
from utils.constants import CHUNK_SIZE

class UDPClient:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start_download(self, server_ip, path):
        self.socket.connect((server_ip, SERVER_PORT))
        self.socket.sendall(self.get_request(path, DOWNLOAD))

        response = self.socket.recv(RESPONSE_STATUS_BYTES)
        if response[0] == 0:
            file_size = int.from_bytes(self.socket.recv(FILE_SIZE_BYTES), byteorder="big")
        else:
            print("Error in download response")
            return

        with open(path, 'wb') as file:
            while file_size > 0:
                offset = int.from_bytes(self.socket.recv(CHUNK_OFFSET_BYTES), byteorder="big")
                chunk_size = int.from_bytes(self.socket.recv(CHUNK_SIZE_BYTES), byteorder="big")
                chunk = self.socket.recv(chunk_size)
                file.write(chunk)
                file_size -= CHUNK_SIZE

    def start_upload(self, server_ip, path):
        self.socket.connect((server_ip, SERVER_PORT))
        self.socket.sendall(self.get_request(path, UPLOAD))
        response = self.socket.recv(RESPONSE_STATUS_BYTES)
        if response[0] == 0:
            with open(path, 'rb') as file:
                file_size = os.path.getsize(path)
                bytes_sent = 0
                while file_size > bytes_sent:
                    data = b''
                    # offset
                    data += bytes_sent.to_bytes(CHUNK_OFFSET_BYTES, byteorder="big")

                    chunk = file.read(CHUNK_SIZE)
                    # chunk size
                    data += len(chunk).to_bytes(CHUNK_SIZE_BYTES, byteorder="big")
                    # chunk
                    data += chunk
                    self.socket.sendall(data)
                    bytes_sent += CHUNK_SIZE
        else:
            print("Error in upload response")
            return

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
