from socket import socket, AF_INET, SOCK_STREAM
from server.src.sockets.TCPSocket import TCPSocket
from constants import PATH_SIZE_BYTES, SERVER_PORT, CHUNK_SIZE_BYTES, CHUNK_OFFSET_BYTES


class Client:
        
    def start_dummy_download(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect(("127.0.0.1", SERVER_PORT))
        s.send(self.get_download_request())
        
        status = s.recv(1)
        if int.from_bytes(status) == 1:
            print("There was an error")
            return

        file_size = int.from_bytes(s.recv(4))

        
        with open("./downloads/test-download.txt", "wb") as f:
            while file_size > 0:
                chunk_offset = int.from_bytes(s.recv(CHUNK_OFFSET_BYTES))
                chunk_size = int.from_bytes(s.recv(CHUNK_SIZE_BYTES))
                data_bytes = s.recv(chunk_size)
                f.write(data_bytes)
                file_size -= len(data_bytes)


    def get_download_request():
        path = b"test-file.txt"

        #Client First Message
        message = b""

        #operation
        message += bytes(0)
        #path size
        message += len(path).to_bytes(PATH_SIZE_BYTES, byteorder="big")
        #path
        message += path

     