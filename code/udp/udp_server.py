import socket
import os

IP_ADDRESS = "172.17.0.2"
PORT = 12342
OBJECTS_DIR = "/root/objects/"


def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP_ADDRESS, PORT))

    print(f"UDP server is listening on {IP_ADDRESS}:{PORT}")

    while True:
        data, client_address = server_socket.recvfrom(1024)
        file_name = data.decode()

        file_path = os.path.join(OBJECTS_DIR, file_name)

        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                file_data = file.read()
                server_socket.sendto(file_data, client_address)
                print(f"Sent {file_name} to {client_address}")
        else:
            error_message = f"Error: File not found - {file_path}"
            server_socket.sendto(error_message.encode(), client_address)
            print(error_message)
            break  # Stop the server after handling one file


if __name__ == "__main__":
    udp_server()
