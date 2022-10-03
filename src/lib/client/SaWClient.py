import os
from socket import SOCK_DGRAM, socket, AF_INET
from lib.client.constants import *
import time
from lib.client.UDPClient import UDPClient
import lib.client.logger as logger

class SaWClient(UDPClient):
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start_download(self, server_ip, path, port, args):
        response, file_size = self.make_request(server_ip, path, DOWNLOAD)
        print(response)
        print(file_size)
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
                    logger.log_connection_failed()
                    return
                try:
                    self.socket.settimeout(5)
                    response, _ = self.socket.recvfrom(PACKET_SIZE)
                    last_ack = time.time()
                    is_error, packet_seq, payload = self.parse_download_response(response)
                except socket.timeout:
                    logger.log_server_not_responding_error(args)
                    continue
                if is_error:
                    logger.log_max_payload_size_exceedes_error(args)
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                elif packet_seq != current_seq:
                    logger.log_packet_sequence_number_error(args)
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                else:
                    current_seq += 1
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                    file.write(payload)
                ack += int(0).to_bytes(PACKET_SIZE - len(ack), "big") # padding
                self.socket.sendto(ack, (server_ip, port))
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
                        logger.log_connection_failed()
                        return
                    self.socket.sendto(data, (server_ip, port))
                    try:
                        self.socket.settimeout(5)
                        acknowledge, _ = self.socket.recvfrom(PACKET_SIZE)
                        acknowledge = acknowledge[:PACKET_SEQUENCE_BYTES] # cut padding
                        last_ack = time.time()
                        if current_seq + 1 == int.from_bytes(acknowledge, byteorder="big"):
                            current_seq += 1
                            break

                    except socket.timeout:
                        logger.log_server_not_responding_error(args)
                        continue

                logger.log_progress((current_seq - 1) * MAX_PAYLOAD_SIZE, file_size, args)
        logger.log_upload_success(path, args)
