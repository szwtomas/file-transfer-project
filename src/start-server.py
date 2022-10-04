from lib.server.GBNServer import GBNServer
from lib.server.Server import Server
from lib.server.SAWServer import SAWServer
from lib.server.parsing import server_args
from lib.server.logger import *

LOG_FILE = "server_log.txt"


def main(host, port, storage, protocol, args):
    init_logger(LOG_FILE)

    # We can optionally accept host and port as command line parameters in the future
    if protocol.lower() == "tcp":
        log_tcp()
        server = Server(host, port, storage)
    elif protocol.lower() == "saw":
        log_saw()
        server = SAWServer(host, port, storage)
    elif protocol.lower() == "gbn":
        log_gbn()
        server = GBNServer(host, port, storage)
    else:
        log_protocol_error(protocol)
        return

    server.run()
    print("Server stopped")


if __name__ == "__main__":
    args = server_args()
    main(args.host, args.port, args.storage, args.protocol, args)
