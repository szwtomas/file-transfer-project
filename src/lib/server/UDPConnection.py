# from concurrent.futures import thread
import threading
import time
from collections import deque
from lib.client.constants import SAW_CONNECTION_MAX_TIME_WITHOUT_MESSAGES
from lib.server.gbn.GBNFileReceiver import GBNFileReceiver
from lib.server.gbn.GBNFileSender import GBNFileSender
from .saw.message_utils import read_until_expected_seq_number
from lib.server.exceptions.MetadataParseException import MetadataParseException
from .metadata.MetadataParser import MetadataParser
from .exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException
from .saw.SAWFileSender import SAWFileSender
from lib.server.saw.SAWFileReceiver import SAWFileReceiver


READ_QUEUE_TIMEOUT = 20
QUEUE_READ_WAITING_TIME_IN_SECONDS = 0.5


class UDPConnection(threading.Thread):

    def __init__(self, client_address, socket, fs_root, protocol):
        threading.Thread.__init__(self)
        self.client_address = client_address
        self.socket = socket
        self.fs_root = fs_root
        self.message_queue = deque()
        self.last_received_message_timestamp = time.time()
        self.metadata_parser = MetadataParser()
        if protocol == "saw":
            self.file_sender = SAWFileSender(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data))
            self.file_receiver = SAWFileReceiver(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data))
        elif protocol == "gbn":
            self.file_sender = GBNFileSender(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data))
            self.file_receiver = GBNFileReceiver(fs_root, lambda: self.read_message_from_queue(), lambda data: self.send_message_to_client(data))
        else:
            print(f"Protocol {protocol} not supported")
            #FIXME: logear

        

    def read_message_from_queue(self):
        timer = time.time()
        while True:
            if time.time() - timer > READ_QUEUE_TIMEOUT:
                raise UDPMessageNotReceivedException("Queue read timeouted")
            if len(self.message_queue) > 0:
                message = self.message_queue.popleft()
                self.last_received_message_timestamp = time.time()
                return message
            time.sleep(QUEUE_READ_WAITING_TIME_IN_SECONDS)


    def enqueue_message(self, message):
        print("encolo mensaje")
        self.message_queue.append(message)


    def run(self):
        self.handle_connection()


    def handle_connection(self):
        try:
            print("Handling connection")
            initial_message = read_until_expected_seq_number(lambda: self.read_message_from_queue(), 0)
            metadata = self.metadata_parser.parse(initial_message)
            print(f"Metadata received from client {self.client_address}: {metadata}")
            if metadata.get_is_download():
                self.handle_download(metadata)
            else:
                self.handle_upload(metadata)
            
        except MetadataParseException as e:
            print(f"UDP Connection: MetadataParseException: {e}")
        except UDPMessageNotReceivedException as e:
            print(f"Seq number error: {e}")
        except Exception as e:
            print(f"UDPConnection Exception: {e}")


    def get_initial_message(self):
        initial_message = self.read_message_from_queue()
        print(f"Initial message: {initial_message}")
        retries = 0 # TODO: Use timers instead of retries
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


    def is_alive(self) -> bool:
        return time.time() - self.last_received_message_timestamp < SAW_CONNECTION_MAX_TIME_WITHOUT_MESSAGES

