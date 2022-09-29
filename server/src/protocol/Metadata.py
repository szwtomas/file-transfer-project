class Metadata:

    def __init__(self, is_download, file_name, file_size, path):
        self.is_download = is_download
        self.file_name = file_name
        self.file_size = file_size
        self.path = path

    def is_download(self) -> bool:
        return self.is_download

    def get_file_name(self) -> str:
        return self.file_name

    def get_file_size(self) -> int:
        return self.file_size

    def get_path(self) -> str:
        return self.path

    def set_is_download(self, is_download):
        self.is_download = is_download

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_file_size(self, file_size):
        self.file_size = file_size
