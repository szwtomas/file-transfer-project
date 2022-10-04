from lib.client.TCPClient import TCPClient
from lib.client.parsing import download_args
from lib.client.GBNClient import GBNClient
from lib.client.SaWClient import SaWClient
from lib.client.logger import *
from lib.client.ClientFactory import ClientFactory
from lib.server.exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException

LOG_FILE = "download_log.txt"


def main(client_factory, args):
    init_logger(LOG_FILE)
    path = args.dst + args.name

    try:
        tcp_client = client_factory.get_client_by_protocol(args.protocol)
        tcp_client.start_download(args.host, path, args.port, args)
    except ProtocolNotSupportedException as e:
        print(f"Protocol not supported exception: {e}")
        log_protocol_error(args.protocol)
    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    args = download_args()
    client_factory = ClientFactory()
    main(client_factory, args)
