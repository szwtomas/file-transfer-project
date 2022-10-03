import os
from socket import SOCK_DGRAM, socket, AF_INET
from constants import *
import time
from UDPClient import UDPClient
import logger

class SaWClient(UDPClient):
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start_download(self, server_ip, path, port, args):
        self.socket.connect((server_ip, SERVER_PORT))
        response, file_size = self.make_request(server_ip, path, DOWNLOAD)
        logger.log_send_download_request(path, args)
        if response == 1:
            logger.log_file_not_found_error(path, args)
            return

        logger.log_file_exists(path, args)
        current_seq = 1
        last_ack = time.time()
        with open(path, 'wb') as file:
            while file_size > (current_seq - 1) * MAX_PAYLOAD_SIZE:
                if time.time() - last_ack > MAX_WAITING_TIME:
                    print("ADD LOGGER ERROR: SERVER TIMEOUT")
                    return
                try:
                    self.socket.settimeout(5)
                    response, _ = self.socket.recvfrom(PACKET_SIZE)
                    last_ack = time.time()
                    is_error, packet_seq, payload = self.parse_download_response(response)
                except socket.timeout:
                    print("Server is not responding")
                    continue
                if is_error or packet_seq != current_seq:
                    print("Error in received packet")
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                else:
                    ack = packet_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                    current_seq += 1
                    file.write(payload)
                ack += int(0).to_bytes(PACKET_SIZE - len(ack), "big") # padding
                self.socket.sendto(ack, (server_ip, SERVER_PORT))
                logger.log_progress((file_size - (current_seq - 1) * MAX_PAYLOAD_SIZE), file_size)
        logger.log_download_success(path, args)

    def start_upload(self, server_ip, path, port, args):
        if not os.path.isfile(path):
            logger.log_file_not_found_client_error(path, args)
            return

        self.socket.connect((server_ip, port))

        response, _ = self.make_request(server_ip, path, UPLOAD)
        logger.log_send_upload_request(path, args)

        if response != 0:  # error
            logger.log_not_enough_space_error(path, args)
            return

        current_seq = 1
        logger.log_start_upload(args)
        with open(path, 'rb') as file:
            file_size = os.path.getsize(path)
            while file_size > (current_seq - 1) * MAX_PAYLOAD_SIZE:
                data = b''
                # packet sequence number
                data += current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")

                chunk = file.read(MAX_PAYLOAD_SIZE)
                # chunk size
                data += len(chunk).to_bytes(PAYLOAD_SIZE_BYTES, byteorder="big")
                # chunk
                data += chunk
                data += int(0).to_bytes(PACKET_SIZE - len(data), "big") # padding
                
                last_ack = time.time()
                while True:
                    if time.time() - last_ack < MAX_WAITING_TIME:
                        print("ADD LOGGER ERROR: SERVER TIMEOUT")
                        return
                    self.socket.sendto(data, (server_ip, SERVER_PORT))
                    try:
                        self.socket.settimeout(5)
                        acknowledge, _ = self.socket.recvfrom(PACKET_SIZE)
                        acknowledge = acknowledge[:PACKET_SEQUENCE_BYTES] # cut padding
                        last_ack = time.time()
                        if current_seq == int.from_bytes(acknowledge, byteorder="big"):
                            current_seq += 1
                            break

                    except socket.timeout:
                        print("Server is not responding")
                        continue

                logger.log_progress((current_seq - 1) * MAX_PAYLOAD_SIZE, file_size, args)
        logger.log_upload_success(path, args)
