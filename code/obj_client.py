#!/usr/bin/env python3

import socket
# import hashlib

IP_ADDRESS = "172.17.0.2"
PORT = 12345

OBJECTS_DIR = "/root/objects/"

# Function to calculate MD5 hash of a file
# def calculate_md5(file_path):
#     md5 = hashlib.md5()
#     with open(file_path, 'rb') as file:
#         for chunk in iter(lambda: file.read(4096), b""):
#             md5.update(chunk)
#     return md5.hexdigest()

# Define the server address and port
server_address = ('172.17.0.2', 12345)

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Connect to the server
    client_socket.connect(server_address)
    print("Connected to the server...")
    received_data = b""
    left, mid, right = b"", b"", b""
    # Function to receive and save objects to files with MD5 hashes
    for i in range(10):
        completed = False
        for size in "large", "small":
            # Receive large object
            received_data = right
            while True:
                chunk = client_socket.recv(1024)  # Adjust buffer size accordingly
                if not chunk:
                    completed = True
                    break
                left, mid, right = chunk.partition(b"=\n")
                if not mid:
                    received_data += chunk
                else:
                    received_data += left + mid
                    break
    
            # Save received object to a file
            with open(OBJECTS_DIR + f'received_{size}-{i}.obj', 'wb') as file:
                file.write(received_data)
            print(f"Received and saved {size} Object {i}")
    
            # Receive and compare MD5 hash for object
            # received_md5 = client_socket.recv(32).decode()
            # calculated_md5 = calculate_md5(OBJECTS_DIR + f'received_{size}-{i}.obj')
            # print(f"Received MD5 hash for {size} Object {i}: {received_md5}")
            # print(f"Calculated MD5 hash for {size} Object {i}: {calculated_md5}")
            # print(f"Hash Match: {received_md5 == calculated_md5}")
