import threading
from collections import deque
from .constants import SAW_PROTOCOL, GBN_PROTOCOL
from .constants import MAX_ALIVE_TIME
import time
from lib.server.gbn.GBNFileReceiver import GBNFileReceiver
from lib.server.gbn.GBNFileSender import GBNFileSender
from .saw.message_utils import read_until_expected_seq_number
from lib.server.exceptions.MetadataParseException import MetadataParseException
from .metadata.MetadataParser import MetadataParser
from .exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException
from .saw.SAWFileSender import SAWFileSender
from lib.server.saw.SAWFileReceiver import SAWFileReceiver
from .exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException

import lib.server.logger as logger

class UDPConnection(threading.Thread):

    def __init__(self, client_address, socket, fs_root, protocol, args):
        threading.Thread.__init__(self)
        self.client_address = client_address
        self.socket = socket
        self.fs_root = fs_root
        self.message_queue = deque()
        self.metadata_parser = MetadataParser()

        self.last_message_read_timestamp = time.time()
        if protocol.lower() == SAW_PROTOCOL:
            self.file_sender = SAWFileSender(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data), args)
            self.file_receiver = SAWFileReceiver(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data), args)
        elif protocol.lower() == GBN_PROTOCOL:
            self.file_sender = GBNFileSender(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data), args)
            self.file_receiver = GBNFileReceiver(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data), args)
        else:
            raise ProtocolNotSupportedException(f"Protocol {protocol} not supported")


    def read_message_from_queue(self):

        self.args = args
        if protocol == "saw":
            self.file_sender = SAWFileSender(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data), args)
            self.file_receiver = SAWFileReceiver(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data), args)
        elif protocol == "gbn":
            self.file_sender = GBNFileSender(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data), args)
            self.file_receiver = GBNFileReceiver(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data), args)
        else:
            logger.log_protocol_error(protocol)


    def read_message_from_queue(self):
        timer = time.time()
        while True:
            if time.time() - timer > 20:
                raise UDPMessageNotReceivedException("Timeout")
            if len(self.message_queue) > 0:
                message = self.message_queue.popleft()
                self.last_message_read_timestamp = time.time()
                return message

            time.sleep(0.15)


    def enqueue_message(self, message):
        self.message_queue.append(message)


    def run(self):
        self.handle_connection()


    def handle_connection(self):
        try:
            initial_message = read_until_expected_seq_number(lambda: self.read_message_from_queue(), 0)
            metadata = self.metadata_parser.parse(initial_message)
            if metadata.get_is_download():
                self.handle_download(metadata)
            else:
                self.handle_upload(metadata)

        except Exception as e:
            logger.log_error(e, self.args)


    def get_initial_message(self):
        initial_message = self.read_message_from_queue()
        retries = 0
        MAX_RETRIES = 10
        while not self.is_metadata_message(initial_message) and retries < MAX_RETRIES:
            initial_message = self.read_message_from_queue()
            retries += 1
        
        return initial_message


    def handle_download(self, metadata):
        self.file_sender.send_file(metadata)
    

    def handle_upload(self, metadata):
        self.file_receiver.receive_file(metadata)


    def is_metadata_message(self, data):
        return int.from_bytes(data[0:4], "big") == 0


    def send_message_to_client(self, data):
        self.socket.sendto(data, self.client_address)


    def is_alive(self):
        return time.time() - self.last_message_read_timestamp < MAX_ALIVE_TIME