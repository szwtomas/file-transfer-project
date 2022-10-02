from lib.client.TCPClient import TCPClient
from lib.client.parsing import upload_args


def main(host, filename):
    tcp_client = TCPClient()
    tcp_client.start_upload(host, filename)


if __name__ == "__main__":
    args = upload_args()
    main(args.host, args.name)

