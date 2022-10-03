import os
from socket import socket, AF_INET, SOCK_STREAM
import lib.client.logger as logger
from lib.server.constants import CHUNK_SIZE
from .constants import *


DOWNLOAD_CONFIRMED_INDEX = 4

class TCPClient:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
    

    def start_download(self, server_ip, path, port, args):
        self.socket.connect((server_ip, port))
        self.socket.sendall(self.get_request(path, DOWNLOAD))
        logger.log_send_download_request(path, args)

        response = self.socket.recv(CHUNK_SIZE)
        seq_number = int.from_bytes(response[0:4], "big")
        print(f"Seq number received: {seq_number}")
        if seq_number != 0:
                print("Wrong sequence number")
                return

        print(f"INTFROMBYTES: {response[4]}")
        download_confirmation = response[4]
        if download_confirmation == 0:
            print("Download confirmed")
            file_size = int.from_bytes(response[5:9], byteorder="big")
            print("File size: ", file_size)
        else:
            logger.log_file_not_found_error(path, args)
            return

        remaining_file_size = file_size
        with open(path, 'wb') as file:
            print(f"path: {path}")
            while file_size > 0:
                # TCP Does not use sequence numbers, so we can discard them
                message_data = self.socket.recv(CHUNK_SIZE)
                print(f"Message Data: {message_data[0:16]}")
                seq_number = int.from_bytes(message_data[0:4], "big")
                payload_size = int.from_bytes(message_data[4:8], "big")
                if payload_size > CHUNK_SIZE - 8:
                    print(f"Invalid payload size: {payload_size}")
                    return
                payload = message_data[8:8 + payload_size]
                print(f"Received payload: {payload}")
                file.write(payload)
                file_size -= payload_size
        logger.log_download_success(path, args)


        """self.socket.sendall(self.get_request(path, UPLOAD))
        logger.log_send_upload_request(path, args)

        response = self.socket.recv(RESPONSE_STATUS_BYTES)

        if response[0] == 0:
            logger.log_start_upload(args)
            with open(path, 'rb') as file:
                file_size = os.path.getsize(path)
                bytes_sent = 0
                while file_size > bytes_sent:
                    data = b''
                    # offset
                    data += bytes_sent.to_bytes(CHUNK_SEQ_NUMBER_BYTES, byteorder="big")
                    
                    chunk = file.read(MAX_PAYLOAD_SIZE)
                    # chunk size
                    data += len(chunk).to_bytes(PAYLOAD_SIZE_BYTES, byteorder="big")
                    # chunk
                    data += chunk
                    self.socket.sendall(data)
                    bytes_sent += MAX_PAYLOAD_SIZE
                    logger.log_progress(bytes_sent, file_size, args)
        else:
            logger.log_not_enough_space_error(path, args)
            return
        logger.log_upload_success(path, args)"""


    def get_request(self, path, operation):
        #Client First Message
        message = b""
        seq_number = 0
        message += seq_number.to_bytes(4, "big")

        #operation
        message += operation.to_bytes(1, byteorder="big")
        #path size
        message += len(path).to_bytes(PATH_SIZE_BYTES, byteorder="big")
        #path
        message += path.encode("UTF-8")
        #file size
        if operation == UPLOAD:
            message += os.path.getsize(path).to_bytes(FILE_SIZE_BYTES, byteorder="big")
        return message

