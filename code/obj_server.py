#!/usr/bin/env python3

import socket


IP_ADDRESS = "172.17.0.2"
PORT = 12345

OBJECTS_DIR = "/root/objects/"


# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the server address
    server_socket.bind((IP_ADDRESS, PORT))

    # Listen for incoming connections
    server_socket.listen(1)
    print("Server is listening for incoming connections...")

    # Accept a connection
    connection, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    for i in range(10):
        for size in "large", "small":
            with open(OBJECTS_DIR + f'{size}-{i}.obj', 'rb') as file:
                data = file.read()

            # Calculate and send MD5 hash of large object
            # with open(OBJECTS_DIR + f'large-{i}.obj.md5', 'rb') as md5_file:
            #     md5 = md5_file.read()

            connection.sendall(data)
            # connection.sendall(md5)
            print(f"Sent {size} Object {i} with precomputed MD5 hash")
            