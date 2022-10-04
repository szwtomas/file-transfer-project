import logging
import traceback
import sys

"""COLOUR CONSTANTS"""
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_RED = '\033[91m'
COLOR_BOLD = '\033[1m'
COLOR_END = '\033[0m'


##############################################################################
# Log init
def init_logger(logging_file):
    logging.basicConfig(filename=logging_file,
                        filemode='w',
                        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] "
                               "%(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


##############################################################################
# Log protocol
def log_tcp():
    logging.info(f"Starting file transfer with TCP")


def log_saw():
    logging.info(f"Starting file transfer with Stop and Wait (UDP)")


def log_gbn():
    logging.info(f"Starting file transfer with Go Back N (UDP)")


##############################################################################
# Upload logs
def log_send_upload_request(file_name, args):
    if args.verbose:
        logging.info(f"Request sent to upload file: {file_name}")
        print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
              f"{COLOR_END} - Request to upload '{file_name}' sent")


def log_start_upload(args):
    if not args.quiet:
        logging.info(f"Starting uploading...")
        print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
              f"{COLOR_END} - Starting uploading...")


def log_packet_seq_number(seq_number, args):
    if args.verbose:
        logging.info(f"Packet number {seq_number} sent.")


def log_upload_success(file_name, args):
    logging.info(f"Finished uploading file: {file_name}")
    print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
          f"{COLOR_END} - Uploaded {file_name} succesfully")


def log_file_not_found_client_error(file_name, args):
    logging.error("Error: The path "
                  f"{file_name} does not exist\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - The file {file_name} does not exist.")


def log_not_enough_space_error(file_name, args):
    logging.error(f"Error: Server does not have enough space for \
                  uploading file: {file_name}\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - Server does not have enough space for uploading file: {file_name}")


##############################################################################
# Download logs
def log_send_download_request(file_name, args):
    if args.verbose:
        logging.info(f"Request sent to download file: {file_name}")
        print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
              f"{COLOR_END} - Request to download '{file_name}' sent")


def log_download_success(file_name, args):
    logging.info("Finished downloading file")
    print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
          f"{COLOR_END} - Downloaded {file_name} successfully")


def log_recv_pack_number(seq_number, args):
    if args.verbose:
        logging.info(f"Received packet number {seq_number}.")


def log_packet_ack_number(ack_number, args):
    if args.verbose:
        logging.info(f"Ack {ack_number} sent.")


def log_file_not_found_error(file_name, args):
    logging.error("Error: The"
                  f"{file_name} does not exist in server\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - The file {file_name} does not exist in server.")


def log_file_exists(file_name, args):
    if not args.quiet:
        logging.info(f"Info: Found file {file_name} on server")
        print(f"{COLOR_BLUE}[INFO]{COLOR_END}"
              f" - Found file {file_name} on server. Starting download")


##############################################################################
# Common errors

def log_packet_sequence_number_error(args):
    if args.verbose:
        logging.info("Packet sequence number is not correct")
        print()
        print(f"{COLOR_BLUE}[INFO]{COLOR_END}"
              " - Packet sequence number is not correct")


def log_max_payload_size_exceedes_error(args):
    if args.verbose:
        logging.error("Packet payload size from received packet exceeded maximum size")
        print(f"{COLOR_RED}[ERROR]{COLOR_END}"
              " - Packet payload size from received packet exceeded maximum size")


def log_server_not_responding_error(args):
    if args.verbose:
        logging.info("Server not responding...")
        print(f"{COLOR_BLUE}[INFO]{COLOR_END}"
              " - Server not responding...")


def log_protocol_error(protocol_name):
    logging.critical(f"Error: The protocol '{protocol_name}' is not valid\nExiting program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - The protocol '{protocol_name}' is not valid,"
          f" please choose between 'TCP', 'SAW' or 'GBN'\n"
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


##############################################################################
# Log progress
def log_progress(bytes_sent, total_bytes):
    progress = int(round(50 * bytes_sent / float(total_bytes)))
    progress_bar = '=' * (progress - 1) + '>' + '.' * (50 - progress)
    percents = round(100.0 * bytes_sent / float(total_bytes), 1)
    if percents > 100:
        percents = 100
    sys.stdout.write(
        f"{COLOR_GREEN}[PROGRESS]{COLOR_END}"
        f": [{progress_bar}] "
        f"{COLOR_BOLD}{percents}%{COLOR_END}\r")
    sys.stdout.flush()
    if bytes_sent >= total_bytes:
        progress_bar = '=' * progress + '.' * (50 - progress)
        sys.stdout.write(
            f"{COLOR_GREEN}[PROGRESS]{COLOR_END}"
            f": [{progress_bar}] "
            f"{COLOR_BOLD}{percents}%{COLOR_END}\r")
        sys.stdout.flush()
        print()
