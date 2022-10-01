
import socket

from TCPClient import TCPClient


def main():
    tcp_client = TCPClient()
    tcp_client.start_download("127.0.0.1", "test.txt")



if __name__ == "__main__":
    main()
