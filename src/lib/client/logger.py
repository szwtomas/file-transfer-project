import logging
import traceback
import sys

"""COLOUR CONSTANTS"""
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_RED = '\033[91m'
COLOR_BOLD = '\033[1m'
COLOR_END = '\033[0m'


def log_send_upload_request(file_name, args):
    logging.info(f"Request sent to upload file: {file_name}")
    print(f"{COLOR_BOLD}{COLOR_GREEN}[INFO]"
          f"{COLOR_END} - Request to upload '{file_name}' sent")


def log_start_upload(args):
    logging.info(f"Starting uploading...")
    print(f"{COLOR_BOLD}{COLOR_GREEN}[INFO]"
          f"{COLOR_END} - Starting uploading...")


def log_upload_success(file_name, args):
    logging.info(f"Finished uploading file: {file_name}")
    print(f"{COLOR_BOLD}{COLOR_GREEN}[INFO]"
          f"{COLOR_END} - Uploaded {file_name} succesfully")


def log_download_success(file_name, args):
    logging.info("Finished downloading file")
    print(f"{COLOR_BOLD}{COLOR_GREEN}[INFO]"
          f"{COLOR_END} - Downloaded {file_name} successfully")


def log_file_not_found_error(file_name, args):
    logging.error("Error: The"
                  f"{file_name} does not exist in server\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - The file {file_name} does not exist in server.")


def log_file_not_found_client_error(file_name, args):
    logging.error("Error: The"
                  f"{file_name} does not exist\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - The file {file_name} does not exist.")


def log_not_enough_space_error(file_name, args):
    logging.error(f"Error: Server does not have enough space for \
                  uploading file: {file_name}\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - Server does not have enough space for uploading file: {file_name}")


def log_packet_sequence_number_error(verbosity, args):
    if verbosity:
        logging.info("Packet sequence number is not correct")
        print(f"{COLOR_RED}[INFO]{COLOR_END}"
              " - Packet sequence number is not correct")


def log_file_exists(file_name, verbosity, args):
    logging.info(f"Info: Found file {file_name} on server")
    if verbosity:
        print(f"{COLOR_BLUE}[INFO]{COLOR_END}"
              f" - Found file {file_name} on server. Starting download")


def log_protocol_error(protocol_name):
    logging.critical(f"Error: The protocol required: {protocol_name} does not exist\nExiting program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - The protocol required: {protocol_name} does not exist\nExiting program - "
          f"Exiting Program")


def log_unknown_exception(args):
    logging.critical(f"There was an unknown Error:\n\n{traceback.format_exc()}"
                     f"\nExiting program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - There was an unknown Error - "
          f"Exiting Program")


def log_connection_refused():
    logging.critical("Error: Conection to the server was refused"
                     "\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          " - Connection to the server refused.")


def log_connection_failed():
    logging.error("Error: Conection to the server has failed. "
                  "\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          " - Connection to the server failed.")


def init_logger(logging_file):
    logging.basicConfig(filename=logging_file,
                        filemode='w',
                        format="[%(asctime)s] [%(levelname)s]\n"
                               "%(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


def log_progress(bytes_sent, total_bytes):
    percents = round(100.0 * bytes_sent / float(total_bytes), 1)
    sys.stdout.write(
        f"{COLOR_GREEN}[PROGRESS]{COLOR_END}"
        f" - {COLOR_BOLD}{percents}%{COLOR_END}\r")
    sys.stdout.flush()
    if bytes_sent == total_bytes:
        print()