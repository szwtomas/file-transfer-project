import os
from socket import socket, AF_INET, SOCK_STREAM
import lib.client.logger as logger
from lib.server.constants import CHUNK_SIZE
from .constants import *

ROOT_FS_PATH = os.getcwd() + "/../client_fs_root/"
DOWNLOAD_CONFIRMED_INDEX = 4

class TCPClient:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
    
    def start_download(self, server_ip, path, port, args):
        complete_path = ROOT_FS_PATH + path
        self.socket.connect((server_ip, port))
        self.socket.sendall(self.get_request(path, DOWNLOAD))
        logger.log_send_download_request(path, args)

        response = self.socket.recv(PACKET_SIZE)
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
        with open(complete_path, 'wb') as file:
            print(f"path: {complete_path}")
            while file_size > 0:
                # TCP Does not use sequence numbers, so we can discard them
                #FIXME: should add timeout?
                try:
                    self.socket.settimeout(SOCKET_TIMEOUT)
                    message_data = self.socket.recv(PACKET_SIZE)
                except socket.timeout:
                    print(f"Server did not responde after {SOCKET_TIMEOUT} seconds")
                    return
                seq_number = int.from_bytes(message_data[0:PACKET_SEQUENCE_BYTES], "big")
                payload_size = int.from_bytes(message_data[PACKET_SEQUENCE_BYTES: PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES], "big")
                if payload_size > MAX_PAYLOAD_SIZE or payload_size <= 0:
                    print(f"Received invalid payload size: {payload_size}")
                    return
                payload = message_data[PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES:PACKET_SEQUENCE_BYTES + PAYLOAD_SIZE_BYTES + payload_size]
                print(f"seq_num: {seq_number}, Received Payload size: {payload_size}")
                file.write(payload)
                file_size -= payload_size

        logger.log_download_success(path, args)

    def start_upload(self, server_ip, path, port, args):
        complete_path = ROOT_FS_PATH + path
        print("Starting upload, path: ", complete_path)
        # check if file exists at same level of src
        if not os.path.isfile(complete_path):
            logger.log_file_not_found_client_error(complete_path, args)
            return

        try:
            self.socket.connect((server_ip, port))
        except ConnectionRefusedError:
            logger.log_connection_refused()
            return

        self.socket.sendall(self.get_request(path, UPLOAD))
        logger.log_send_upload_request(path, args)

        response = self.socket.recv(PACKET_SIZE)

        if response[0] == 0:
            logger.log_start_upload(args)
            with open(complete_path, 'rb') as file:
                file_size = os.path.getsize(complete_path)
                bytes_sent = 0
                seq_number = 0
                while file_size > bytes_sent:
                    data = b''
                    # offset
                    data += seq_number.to_bytes(PACKET_SEQUENCE_BYTES,          byteorder="big")
                    
                    payload = file.read(MAX_PAYLOAD_SIZE)
                    # payload size
                    data += len(payload).to_bytes(PAYLOAD_SIZE_BYTES, byteorder="big")
                    # chunk
                    data += payload
                    data += int(0).to_bytes(PACKET_SIZE - len(data),
                    byteorder="big")
                    self.socket.sendall(data)
                    bytes_sent += MAX_PAYLOAD_SIZE
                    logger.log_progress(bytes_sent, file_size)
                    seq_number += 1
        else:
            logger.log_not_enough_space_error(path, args)
            return
        logger.log_upload_success(path, args)


    def get_request(self, path, operation):
        #Client First Message
        message = b""
        seq_number = 0
        message += seq_number.to_bytes(PACKET_SEQUENCE_BYTES, "big")

        #operation
        message += operation.to_bytes(OPERATION_BYTES, byteorder="big")
        #path size
        message += len(path).to_bytes(PATH_SIZE_BYTES, byteorder="big")
        #path
        message += path.encode("UTF-8")
        #file size
        if operation == UPLOAD:
            message += os.path.getsize(ROOT_FS_PATH + path).to_bytes(FILE_SIZE_BYTES, byteorder="big")
            
        message += int(0).to_bytes(PACKET_SIZE - len(message),
                    byteorder="big")
        return message

