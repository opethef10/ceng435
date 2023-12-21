# echo-server.py
import socket

# create tcp/ip socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# set so_reuseaddr option
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ip_addr = "172.17.0.2"
port_num = 12345

server.bind((ip_addr, port_num))

server.listen(1)

print(f"Server listening the : {ip_addr}:{port_num}")

while True:
    print("Waiting for a connection...")
    connection, address = server.accept()
    print(f"Connected to {address}")

    # logic
    data = connection.recv(1024)  # max 1024 bytes

    # process data

    # response
    connection.sendall(b"Request received: " + data)

    connection.close()
