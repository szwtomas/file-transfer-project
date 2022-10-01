import os
from sockets import TCPSocket
from constants import MAX_FILE_SIZE_SUPPORTED_IN_BYTES, ERROR_BYTES
from exceptions import FileDoesNotExistException, FileSizeNotSupportedException


class FileTransferValidator:

    def send_invalid_download_message(self, socket: TCPSocket):
        socket.send_data(ERROR_BYTES)


    def send_invalid_operation_message(self, socket: TCPSocket):
        socket.send_data(ERROR_BYTES)


    def verify_valid_file_size(self, socket: TCPSocket, file_size: int):
        if file_size > MAX_FILE_SIZE_SUPPORTED_IN_BYTES:
            self.send_invalid_operation_message(socket)
            error_message = f"File size {file_size} is not supported, max file size is {MAX_FILE_SIZE_SUPPORTED_IN_BYTES}"
            raise FileSizeNotSupportedException(error_message)


    def verify_valid_path(self, socket: TCPSocket, file_path: str):
        '''
        TODO: Maybe add some regex verification to check if path syntax is valid
        '''
        if not os.path.isfile(file_path):
            error_message = f"File {file_path} does not exist"
            print(error_message)
            self.send_invalid_download_message(socket)
            raise FileDoesNotExistException(error_message)

