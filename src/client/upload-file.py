from TCPClient import TCPClient


def main():
    tcp_client = TCPClient()
    tcp_client.start_upload("127.0.0.1", "image.png")



if __name__ == "__main__":
    main()
