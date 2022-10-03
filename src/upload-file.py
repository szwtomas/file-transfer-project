from lib.client.TCPClient import TCPClient
from lib.client.parsing import upload_args
from lib.client.logger import *
from src.lib.client.GBNClient import GBNClient
from src.lib.client.SaWClient import SaWClient

LOG_FILE = "upload_log.txt"


def main(args):
    init_logger(LOG_FILE)

    path = args.src + args.name

    if args.protocol == "TCP":
        tcp_client = TCPClient()
        tcp_client.start_upload(args.host, path, args.port, args)

    elif args.protocol == "SAW":
        saw_client = SaWClient()
        saw_client.start_upload(args.host, path, args.port, args)

    elif args.protocol == "GBN":
        gbn_client = GBNClient()
        gbn_client.start_upload(args.host, path, args.port, args)

    else:
        log_protocol_error(args.protocol)


if __name__ == "__main__":
    args = upload_args()
    main(args)

