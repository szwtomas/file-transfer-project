import logging
import traceback

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
                        format="[%(asctime)s] [%(levelname)s] "
                               "%(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


##############################################################################
# Log protocol
def log_tcp():
    logging.info(f"Starting TCP Server")


def log_saw():
    logging.info(f"Starting Stop and Wait Server (UDP)")


def log_gbn():
    logging.info(f"Starting Go Back N Server (UDP)")


##############################################################################
# Upload logs
def log_incoming_upload_request(ip, file_name, args):
    if not args.quiet:
        logging.info(f"Incoming request from {ip} to upload file: {file_name}")
        print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
              f"{COLOR_END} - Incoming request to upload '{file_name}' from {ip}")


def log_start_upload(ip, args):
    if not args.quiet:
        logging.info(f"Starting uploading file from {ip}")
        print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
              f"{COLOR_END} - Starting uploading file from {ip}")


def log_packet_seq_number(ip, seq_number, args):
    if args.verbose:
        logging.info(f"Packet number {seq_number} received from {ip}")


def log_upload_success(ip, file_name, args):
    logging.info(f"Finished uploading file '{file_name}' from {ip}")
    print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
          f"{COLOR_END} - Uploaded {file_name} succesfully")


def log_not_enough_space_error(ip, file_name, args):
    logging.error(f"Error: Server does not have enough space for \
                  uploading file: {file_name}. Stop uploading...")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - Server does not have enough space for uploading file: {file_name}. Stop uploading...")


##############################################################################
# Download logs
def log_incoming_download_request(ip, file_name, args):
    if not args.quiet:
        logging.info(f"Incoming request from {ip} to download file: {file_name}")
        print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
              f"{COLOR_END} - Incoming request to download '{file_name}' from {ip}")


def log_download_success(ip, file_name, args):
    logging.info(f"CLient {ip} finished downloading file {file_name}")
    print(f"{COLOR_BOLD}{COLOR_BLUE}[INFO]"
          f"{COLOR_END} - Downloaded {file_name} successfully")


def log_send_pack_number(ip, seq_number, args):
    if args.verbose:
        logging.info(f"Sending packet number {seq_number} to {ip}")


def log_file_not_found_error(ip, file_name, args):
    logging.error("Error: The file "
                  f"'{file_name}' requested by {ip} does not exist in server. Stop downloading...")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          f" - The file {file_name} requested by {ip} does not exist in server. Stop downloading...")


def log_file_exists(ip, file_name, args):
    if not args.quiet:
        logging.info(f"Info: Found file {file_name} on server")
        print(f"{COLOR_BLUE}[INFO]{COLOR_END}"
              f" - Found file {file_name} on server. Starting sending to {ip}")


##############################################################################
# Common errors

def log_packet_sequence_number_error(ip, args):
    if args.verbose:
        logging.info(f"Packet sequence number from {ip} is not correct")
        print()
        print(f"{COLOR_BLUE}[INFO]{COLOR_END}"
              f" - Packet sequence number from {ip} is not correct")


def log_max_payload_size_exceedes_error(ip, args):
    if args.verbose:
        logging.error(f"Packet payload size from {ip} exceeded maximum size")
        print(f"{COLOR_RED}[ERROR]{COLOR_END}"
              f" - Packet payload size from {ip} exceeded maximum size")


def log_client_not_responding_error(ip, args):
    if args.verbose:
        logging.info(f"Client {ip} not responding...")
        print(f"{COLOR_BLUE}[INFO]{COLOR_END}"
              f" - Client {ip} not responding...")


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


def log_connection_failed():
    logging.error("Error: Conection to the server has failed. "
                  "\nExiting Program")
    print(f"{COLOR_RED}[ERROR]{COLOR_END}"
          " - Connection to the server failed.")
