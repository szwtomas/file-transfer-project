from socket import socket, AF_INET, SOCK_STREAM

PORT = 7878

s = socket(AF_INET, SOCK_STREAM)
s.connect(("127.0.0.1", PORT))
s.send("Hello world".encode())
data = s.recv(1024)
print(data.decode())