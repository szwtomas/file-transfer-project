from pickletools import bytes1

from Metadata import Metadata

class MetadataParser:
    
    # Receives bytes with the following headers:
    # 1 byte: is_download (0 means download, 1 means upload)
    # 1 byte: file_name length in bytes (filename cant be longer than 255 bytes)
    # file_name: the name of the file, of length file_name_length
    # 4 bytes: file_size (Max file size is 4GB)
    # 1 byte: path length in bytes (path cant be longer than 255 bytes)
    # path: the path of the file, of length path_length
    def parse(self, data) -> Metadata:
        is_download = self.parse_is_download(data)
        file_name = self.parse_file_name(data)
        file_size = self.parse_file_size(data)
        path = self.parse_path(data)
        return Metadata(is_download, file_name, file_size, path)

    def parse_is_download(self, data) -> bool:
        return data[0] == 0

    def parse_file_name(self, data) -> str:
        file_name_length = data[1]
        file_name = data[2:2 + file_name_length]
        return file_name.decode("utf-8")

    def parse_file_size(self, data) -> int:
        file_size = data[2 + data[1]:6 + data[1]]
        return int.from_bytes(file_size, byteorder="big")

    def parse_path(self, data) -> str:
        path_length = data[6 + data[1]]
        path = data[7 + data[1]:7 + data[1] + path_length]
        return path.decode("utf-8")

