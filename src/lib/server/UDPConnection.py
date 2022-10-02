import threading
from collections import deque

from lib.server.exceptions.MetadataParseException import MetadataParseException
from .metadata.MetadataParser import MetadataParser

class UDPConnection(threading.Thread):

    def __init__(self, client_address, socket, fs_root):
        self.client_address = client_address
        self.socket = socket
        self.fs_root = fs_root
        self.message_queue = deque()
        self.metadata_parser = MetadataParser()


    def read_message_from_queue(self):
        return self.message_queue.popleft()

    def enqueue_message(self, message):
        self.message_queue.append(message)

    def run(self):
        self.handle_connection()

    def handle_connection(self):
        try:
            initial_message = self.read_message_from_queue()
            print(f"Initial message: {initial_message}")
            metadata = self.metadata_parser.parse_metadata(initial_message)
            print(f"Metadata received from client {self.client_address}: {metadata}")
            if metadata.is_download():
                self.handle_download(metadata)
            else:
                self.handle_upload(metadata)
        except MetadataParseException as e:
            print(f"UDP Connection: MetadataParseException: {e}")
            return
        except Exception as e:
            print(f"UDPConnection Exception: {e}")

    def handle_download(self, metadata):
        print(f"Handling download for metadata: {metadata}")
        