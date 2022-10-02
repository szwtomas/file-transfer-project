import threading
from collections import deque
from .saw.message_utils import read_until_expected_seq_number
from lib.server.exceptions.MetadataParseException import MetadataParseException
from .metadata.MetadataParser import MetadataParser
from .exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException
from .saw.SAWFileSender import SAWFileSender

class UDPConnection(threading.Thread):

    def __init__(self, client_address, socket, fs_root):
        self.client_address = client_address
        self.socket = socket
        self.fs_root = fs_root
        self.message_queue = deque()
        self.metadata_parser = MetadataParser()
        self.file_sender = SAWFileSender(fs_root, lambda: self.read_message_from_queue(), lambda: self.send_message_to_client())


    def read_message_from_queue(self):
        return self.message_queue.popleft()


    def enqueue_message(self, message):
        self.message_queue.append(message)


    def run(self):
        self.handle_connection()


    def handle_connection(self):
        try:
            initial_message = read_until_expected_seq_number(lambda: self.read_message_from_queue(), 0)
            metadata = self.metadata_parser.parse_metadata(initial_message)
            print(f"Metadata received from client {self.client_address}: {metadata}")
            if metadata.is_download():
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
        print(f"Handling download for metadata: {metadata}")
    

    def is_metadata_message(self, data):
        return int.from_bytes(data[0:4]) == 0


    def send_message_to_client(self, data):
        self.socket.sendto(data, self.client_address)

