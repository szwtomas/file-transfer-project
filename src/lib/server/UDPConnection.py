# from concurrent.futures import thread
import threading
from collections import deque
import time

from lib.client.constants import MAX_WAITING_TIME
from lib.server.gbn.GBNFileReceiver import GBNFileReceiver
from lib.server.gbn.GBNFileSender import GBNFileSender
from .saw.message_utils import read_until_expected_seq_number
from lib.server.exceptions.MetadataParseException import MetadataParseException
from .metadata.MetadataParser import MetadataParser
from .exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException
from .saw.SAWFileSender import SAWFileSender
from lib.server.saw.SAWFileReceiver import SAWFileReceiver

class UDPConnection(threading.Thread):

    def __init__(self, client_address, socket, fs_root, protocol):
        threading.Thread.__init__(self)
        self.client_address = client_address
        self.socket = socket
        self.fs_root = fs_root
        self.message_queue = deque()
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

        

    def read_message_from_queue(self): # si queremos que sea bloqueante tiene que estar en while
        print("espero a leer mensaje")
        timer = time.time()
        while True:
            if time.time() - timer > 20:
                raise UDPMessageNotReceivedException("Timeout")
            if len(self.message_queue) > 0:
                print("desencolo mensaje")
                return self.message_queue.popleft()
            # time.sleep(0.01)

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
        print(f"Handling download for metadata: {metadata}")
        self.file_sender.send_file(metadata)
    
    def handle_upload(self, metadata):
        print(f"Handling upload for metadata: {metadata}")
        self.file_receiver.receive_file(metadata)

    def is_metadata_message(self, data):
        return int.from_bytes(data[0:4], "big") == 0

    def send_message_to_client(self, data):
        self.socket.sendto(data, self.client_address)
