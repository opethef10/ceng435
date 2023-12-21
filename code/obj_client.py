# echo-client.py

import socket

HOST = "172.17.0.2"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"small-0.obj")
    data = s.recv(10240)

print(data)