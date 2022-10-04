import threading
from .metadata.MetadataParser import MetadataParser
from .file_transfer.FileReceiver import FileReceiver
from .file_transfer.FileSender import FileSender
from .sockets.TCPSocket import TCPSocket
import lib.server.logger as logger

class TCPConnection(threading.Thread):
    
    def __init__(self, socket: TCPSocket, fs_root, args):
        threading.Thread.__init__(self)
        self.socket = socket
        self.fs_root = fs_root
        self.metadata_parser = MetadataParser()
        self.file_sender = FileSender(fs_root, args)
        self.file_receiver = FileReceiver(fs_root, args)
        self.args = args
        

    def run(self):
        self.handle_connection()


    def handle_connection(self):
        try:
            data = self.socket.read_data()
            metadata = self.metadata_parser.parse(data)
            self.transfer_file(metadata)
        except Exception as e:
            logger.log_handle_connection_error(e)


    def transfer_file(self, metadata):
        try:
            if metadata.get_is_download():
                self.file_sender.send_file(self.socket, metadata)
            else:
                self.file_receiver.receive_file(self.socket, metadata)
        except Exception as e:
            logger.log_error(e, self.args)


    
    def stop_running(self):
        self.socket.close()