from socket import socket as create_socket, AF_INET, SOCK_DGRAM

def create_udp_socket():
    return create_socket(AF_INET, SOCK_DGRAM)