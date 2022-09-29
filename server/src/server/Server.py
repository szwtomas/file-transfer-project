from protocol.MetadataParser import MetadataParser
from protocol.FileSender import FileSender
from protocol.FileReceiver import FileReceiver

class Server:

    def __init__(self, port):
        self.port = port
        self.metadata_parser = MetadataParser()
        self.file_sender = FileSender()
        self.file_receiver = FileReceiver()

    # TODO: Implement concurrently with a threadpool or something
    def start(self):
        '''
        Starts the server, listents indefinitely for connections and handles
        the requests. 
        '''
        while True:
            socket = self.get_connection()
            data = socket.read_data()
            metadata = self.metadata_parser.parse(data)
            if metadata.is_download():
                self.send_file_to_client(socket, metadata)
            else:
                self.receive_file_from_client(socket, metadata)


    def send_file_to_client(self, socket, metadata): 
        self.file_sender.send_file(socket, metadata)

    def receive_file_from_client(self, socket, metadata):
        self.file_receiver.receive_file(socket, metadata)
