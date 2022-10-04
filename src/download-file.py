from lib.client.parsing import download_args
from lib.client.logger import *
from lib.client.ClientFactory import ClientFactory
from lib.server.exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException


LOG_FILE = "download_log.txt"


def main(args, client_factory):
    init_logger(LOG_FILE)
    path = args.dst + args.name
    try:
        client = client_factory.get_client_by_protocol(args.protocol.lower())
        client.start_download(args.host, args.port, args.name, path)
    except ProtocolNotSupportedException as e:
        log_protocol_error(args.protocol)
        print(f"Protocol not supported exception: {e}")


if __name__ == "__main__":
    args = download_args()
    client_factory = ClientFactory()
    main(args, client_factory)
