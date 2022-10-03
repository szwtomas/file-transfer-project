import argparse
from .constants import LOCALHOST, LISTEN_PORT
import os


SERVER_FS_ROOT = os.getcwd() + "/../fs_root"


def server_args():
    parser = argparse.ArgumentParser(description='Server for uploading and downloading files with secure file transfer',
                                     usage="%(prog)s [-h] [-v | -q] [-H ADDR] [-p PORT] [-s DIRPATH] PROTOCOL")

    parser.add_argument("protocol",
                        metavar="PROTOCOL",
                        type=str,
                        help="protocol in use")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v",
                       "--verbose",
                       metavar="",
                       help="increase output verbosity")
    group.add_argument("-q",
                       "--quiet",
                       metavar="",
                       help="decrease output verbosity")

    parser.add_argument("-H",
                        "--host",
                        metavar="",
                        type=str,
                        default=LOCALHOST,
                        help="service IP address")
    parser.add_argument("-p",
                        "--port",
                        metavar="",
                        type=int,
                        default=LISTEN_PORT,
                        help="service port")

    parser.add_argument("-s",
                        "--storage",
                        metavar="",
                        type=str,
                        default=SERVER_FS_ROOT,
                        help="storage dir path")

    args = parser.parse_args()
    return args
