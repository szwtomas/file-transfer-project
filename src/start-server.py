from lib.server.Server import Server
from lib.server.parsing import server_args


def main(host, port, storage):
    # We can optionally accept host and port as command line parameters in the future
    server = Server(host, port, storage)
    server.run()


if __name__ == "__main__":
    args = server_args()
    main(args.host, args.port, args.storage)