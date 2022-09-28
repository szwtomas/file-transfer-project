from MetadataParser import MetadataParser
from FileSender import FileSender
from FileReceiver import FileReceiver

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
                self.download_file(socket, metadata)
            else:
                self.upload_file(socket, metadata)

    def get_connection(self):
        # Implemented by each subclass
        pass

    def send_file_to_client(self): 
        self.file_sender.send_file()

    def receive_file_from_client(self):
        self.file_receiver.receive_file()