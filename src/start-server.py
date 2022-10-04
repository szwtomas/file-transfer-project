from lib.server.ServerFactory import ServerFactory
from lib.server.parsing import server_args
from lib.server.logger import init_logger, log_protocol_error
from lib.server.exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException

LOG_FILE = "server_log.txt"


def main(protocol, server_factory):
    init_logger(LOG_FILE)
    try:
        start_logging = server_factory.get_logger(protocol)
        start_logging()
        server = server_factory.get_server(protocol)
        server.run()
    except ProtocolNotSupportedException as e:
        print(f"Protocol not supported exception: {e}")
        log_protocol_error(protocol)

    print("Server Stopped")
    

if __name__ == "__main__":
    args = server_args()
    host = args.host
    port = args.port
    storage = args.storage
    protocol = args.protocol
    server_factory = ServerFactory(host, port, storage)
    main(args.protocol, server_factory)
