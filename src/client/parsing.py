import argparse
from constants import SERVER_PORT


def upload_args():
    parser = argparse.ArgumentParser(description='Application for downloading files with secure file transfer',
                                     usage="%(prog)s [-h] [-v | -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME] PROTOCOL")

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
                        default="127.0.0.1",
                        help="server IP address")
    parser.add_argument("-p",
                        "--port",
                        metavar="",
                        type=int,
                        default=SERVER_PORT,
                        help="server port")
    parser.add_argument("-s",
                        "--src",
                        metavar="",
                        type=str,
                        default="./",
                        help="source file path")
    parser.add_argument("-n",
                        "--name",
                        metavar="",
                        type=str,
                        default="",
                        help="file name")

    args = parser.parse_args()
    return args
