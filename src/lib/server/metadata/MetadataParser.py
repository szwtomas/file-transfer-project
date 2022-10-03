from ..exceptions.EmptyPathException import EmptyPathException
from .Metadata import Metadata
from ..exceptions.MetadataParseException import MetadataParseException

SEQ_NUMBER_BYTES = 4
FILE_SIZE_BYTES = 4
IS_DOWNLOAD_INDEX = 4
PATH_LENGTH_INDEX = 5
PATH_INDEX = 6

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
            sequence_number = self.parse_sequence_number(data)
            if sequence_number != 0:
                raise MetadataParseException(f"Error parsing metadata: Sequence number is {sequence_number} instad of 0")
            is_download = self.parse_is_download(data)
            print(f"Is Download: {is_download}") 
            path, path_length_in_bytes = self.parse_path(data)
            print(f"path: {path}")
            metadata = Metadata(is_download, path, 0 if is_download else self.parse_file_size(data, path_length_in_bytes))
            print(f"Received Metadata: {metadata}")
            return metadata
        except Exception as e:
            raise MetadataParseException("Error parsing metadata: " + str(e))


    def parse_sequence_number(self, data) -> int:
        return int.from_bytes(data[0 : SEQ_NUMBER_BYTES], "big")


    def parse_is_download(self, data) -> bool:
        return data[IS_DOWNLOAD_INDEX] == 0


    def parse_path(self, data) -> tuple[str, int]:
        path_length = data[PATH_LENGTH_INDEX]
        path = data[PATH_INDEX : PATH_INDEX + path_length]
        if len(path) == 0:
            raise EmptyPathException("Path is empty")            
        return path.decode("utf-8"), path_length


    def parse_file_size(self, data, path_length_in_bytes) -> int:
        file_size_start = PATH_INDEX + path_length_in_bytes
        return int.from_bytes(data[file_size_start : file_size_start + FILE_SIZE_BYTES], byteorder="big")