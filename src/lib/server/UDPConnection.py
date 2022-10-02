import threading
from collections import deque

class UDPConnection(threading.Thread):

    def __init__(self):
        self.message_queue = deque()


    def enqueue_message(self, message):
        self.message_queue.append(message)

    def run():
        print("UDP Connection running")
        # TODO: Implement all (?)