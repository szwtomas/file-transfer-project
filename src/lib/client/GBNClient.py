from io import BufferedReader
import os
from socket import SOCK_DGRAM, socket, AF_INET, timeout
from lib.client.constants import *
import time
from lib.client.UDPClient import UDPClient
import lib.client.logger as logger

ROOT_FS_PATH = os.getcwd() + "/../client_fs_root/"

class GBNClient(UDPClient):
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start_download(self, server_ip, path, port, args):
        logger.log_gbn()
        complete_path = ROOT_FS_PATH + path
        response, file_size = self.make_request(server_ip, path, DOWNLOAD)
        logger.log_send_download_request(path, args)
        if response == 1:
            logger.log_file_not_found_error(path, args)
            return
        logger.log_file_exists(path, args)
        last_ack = time.time()
        with open(complete_path, 'wb') as file:
            current_seq = 1
            while file_size > (current_seq - 1) * MAX_PAYLOAD_SIZE:
                if time.time() - last_ack > MAX_WAITING_TIME:
                    logger.log_connection_failed()
                    return
                try:
                    self.socket.settimeout(5)
                    response, _ = self.socket.recvfrom(PACKET_SIZE)
                    last_ack = time.time()
                    is_error, seq_num, payload = self.parse_download_response(response)
                except timeout:
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                    ack += int(0).to_bytes(PACKET_SIZE - len(ack), "big") # padding
                    self.socket.sendto(ack, (server_ip, port))
                    logger.log_server_not_responding_error(args)
                    continue
                if is_error:
                    logger.log_max_payload_size_exceedes_error(args)
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                elif seq_num > current_seq:
                    logger.log_packet_sequence_number_error(args)
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                elif seq_num < current_seq:
                    logger.log_packet_sequence_number_error(args)
                    continue
                else:
                    current_seq += 1
                    ack = current_seq.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
                    file.write(payload)
                    
                ack += int(0).to_bytes(PACKET_SIZE - len(ack), "big") # padding
                self.socket.sendto(ack, (server_ip, port))
                # print("sent ack", ack[:8])
                print("current seq", current_seq)
                logger.log_progress((current_seq - 1) * MAX_PAYLOAD_SIZE, file_size)
        logger.log_download_success(path, args)


    def start_upload(self, server_ip, path, port, args):
        logger.log_gbn()
        complete_path = ROOT_FS_PATH + path
        if not os.path.isfile(complete_path):
            logger.log_file_not_found_client_error(complete_path, args)
            return
        response, _ = self.make_request(server_ip, path, UPLOAD)
        logger.log_send_upload_request(path, args)
        if response != 0: #error
            logger.log_not_enough_space_error(path, args)
            return
        
        last_acked_recv = 1
        next_seq_to_send = 1
        logger.log_start_upload(args)
        with open(complete_path, 'rb') as file:
            file.seek(0)
            file_size = os.path.getsize(complete_path)
            expected_final_ack = file_size // MAX_PAYLOAD_SIZE + 2

            global_timer = time.time()
            while last_acked_recv < expected_final_ack:
                if  time.time() - global_timer > MAX_WAITING_TIME * 4:
                    print("timed out waiting for ack, exiting program")
                    #FIXME: logggg
                    return
                self.send_n_packets(last_acked_recv, GBN_WINDOW_SIZE, file, server_ip, port)
                next_seq_to_send = last_acked_recv + GBN_WINDOW_SIZE

                last_ack_time = time.time()
                while time.time() - last_ack_time < 2:
                    try:
                        self.socket.settimeout(3)
                        acknowledge, _ = self.socket.recvfrom(PACKET_SIZE)
                        recv_seq_num = int.from_bytes(acknowledge[:PACKET_SEQUENCE_BYTES], "big") # cut padding
                        print("received ack", recv_seq_num)
                        if recv_seq_num < last_acked_recv:
                            continue  # ignore old acks
                        if recv_seq_num == last_acked_recv:
                            print("Probably packet lost")
                            break  # To send again in line 90
                        window_increment = recv_seq_num - last_acked_recv
                        print("window increment", window_increment)
                        last_acked_recv = recv_seq_num
                        last_ack_time = time.time()
                        global_timer = time.time()
                        logger.log_progress((last_acked_recv - 1) * MAX_PAYLOAD_SIZE, file_size)
                        if recv_seq_num == expected_final_ack:
                            break
                        self.send_n_packets(next_seq_to_send, window_increment, file, server_ip, port)
                        next_seq_to_send = next_seq_to_send + window_increment
                    except timeout:
                        logger.log_server_not_responding_error(args)
                        continue
            logger.log_upload_success(path, args)

    def send_n_packets(self, initial, n, file: BufferedReader, server_ip, port):
        '''
        Sends n packets starting from initial sequence number 
        '''
        for seq_num in range(initial, initial + n):
            data = b''
            # sequence number
            print("sending seq", seq_num)
            data += seq_num.to_bytes(PACKET_SEQUENCE_BYTES, byteorder="big")
            file.seek((seq_num - 1) * MAX_PAYLOAD_SIZE)
            chunk = file.read(MAX_PAYLOAD_SIZE)
            if not chunk:
                break

            # chunk size
            data += len(chunk).to_bytes(PAYLOAD_SIZE_BYTES, byteorder="big")
            # chunk
            data += chunk
            data += int(0).to_bytes(PACKET_SIZE - len(data), "big") # padding
            self.socket.sendto(data, (server_ip, port))
