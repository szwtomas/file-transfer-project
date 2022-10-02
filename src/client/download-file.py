from TCPClient import TCPClient
from parsing import download_args


def main(host, filename):
    tcp_client = TCPClient()
    tcp_client.start_download(host, filename)



if __name__ == "__main__":
    args = download_args()
    main(args.host, args.name)
