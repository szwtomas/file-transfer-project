class Metadata:

    def __init__(self, is_download, path, file_size=0):
        self.is_download = is_download
        self.file_size = file_size
        self.path = path


    def get_is_download(self) -> bool:
        return self.is_download


    def get_file_size(self) -> int:
        return self.file_size


    def get_path(self) -> str:
        return self.path


    def __str__(self):
        str_representation = f"is_download: {self.is_download} --- Path: {self.path} --- FileSize: {self.file_size}"
        return str_representation