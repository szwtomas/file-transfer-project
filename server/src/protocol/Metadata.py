class Metadata:

    def __init__(self, is_download, path, file_size=0):
        self.is_download = is_download
        self.file_size = file_size
        self.path = path

    def is_download(self) -> bool:
        return self.is_download

    def get_file_size(self) -> int:
        return self.file_size

    def get_path(self) -> str:
        return self.path
