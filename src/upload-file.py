from lib.client.TCPClient import TCPClient
from lib.client.parsing import upload_args
from lib.client.logger import *
from lib.client.GBNClient import GBNClient
from lib.client.SaWClient import SaWClient
from lib.client.ClientFactory import ClientFactory
from lib.server.exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException


LOG_FILE = "upload_log.txt"


def main(args, client_factory):
    init_logger(LOG_FILE)
    path = args.src + args.name

    try:
        tcp_client = client_factory.get_client_by_protocol(args.protocol)
        tcp_client.start_upload(args.host, path, args.port, args)
    except ProtocolNotSupportedException as e:
        print(f"Protocol not supported exception: {e}")
        log_protocol_error(args.protocol)
    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    args = upload_args()
    client_factory = ClientFactory()
    main(args, client_factory)

