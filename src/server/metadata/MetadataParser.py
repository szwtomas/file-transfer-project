from server.exceptions.EmptyPathException import EmptyPathException
from .Metadata import Metadata
from exceptions import MetadataParseException

class MetadataParser:

    def parse(self, data) -> Metadata:
        '''
        Receives bytes with the following headers:
        1 byte: is_download (0 means download, 1 means upload)
        1 byte: path length in bytes (path cant be longer than 255 bytes)
        path: the path of the file, of length path_length
        4 bytes: file size (only for uploads)
        '''
        try:
            is_download = self.parse_is_download(data)
            print(f"Is Download: {is_download}") 
            path = self.parse_path(data)
            print(f"path: {path}")
            metadata = Metadata(is_download, path, 0 if is_download else self.parse_file_size(data))
            print(f"Received Metadata: {metadata}")
            return metadata
        except Exception as e:
            raise MetadataParseException("Error parsing metadata: " + str(e))


    def parse_is_download(self, data) -> bool:
        return data[0] == 0


    def parse_path(self, data) -> str:
        path_length = data[1]
        path = data[2:2 + path_length]
        if len(path) == 0:
            raise EmptyPathException("Path is empty")            
        return path.decode("utf-8")


    def parse_file_size(self, data) -> int:
        return int.from_bytes(data[2 + data[1]:6 + data[1]], byteorder="big")