from lib.server.parsing import server_args
from lib.server.constants import LOG_FILE_PATH
from lib.server.logger import init_logger
from lib.server.ProtocolServerFactory import ProtocolServerFactory
from lib.server.exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException


def start_logging(protocol_logger):
    init_logger(LOG_FILE_PATH)
    protocol_logger()


def main(host, port, storage, protocol, args, protocol_server_factory):
    init_logger(LOG_FILE_PATH)
    start_logging(protocol_server_factory.get_protocol_logger(protocol))
    try:
        server = protocol_server_factory.get_server_from_selected_protocol(protocol)
        server.run()
    except ProtocolNotSupportedException as e:
        print(f"Protocol not supported exception: {e}")


if __name__ == "__main__":
    args = server_args()
    protocol_server_factory = ProtocolServerFactory()
    main(args.host, args.port, args.storage, args.protocol, args)
