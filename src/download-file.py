from lib.client.TCPClient import TCPClient
from lib.client.parsing import download_args
from lib.client.GBNClient import GBNClient
from lib.client.SaWClient import SaWClient
from lib.client.logger import *

LOG_FILE = "download_log.txt"


def main(args):
    init_logger(LOG_FILE)

    path = args.dst + args.name

    if args.protocol.lower() == "tcp":
        tcp_client = TCPClient()
        tcp_client.start_download(args.host, path, args.port, args)

    elif args.protocol.lower() == "saw":
        saw_client = SaWClient()
        saw_client.start_download(args.host, path, args.port, args)

    elif args.protocol.lower() == "gbn":
        gbn_client = GBNClient()
        gbn_client.start_download(args.host, path, args.port, args)

    else:
        log_protocol_error(args.protocol)


if __name__ == "__main__":
    args = download_args()
    main(args)
