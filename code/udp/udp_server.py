import socket
import os

IP_ADDRESS = "0.0.0.0"
PORT = 45404
# OBJECTS_DIR = "/root/objects/"
OBJECTS_DIR = "../../objects/"

BUFFER_SIZE = 1024  # Adjust the buffer size according to your needs


def udp_server():
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set the socket options to allow quick reuse of the socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    # Bind the socket to the IP address and port
    server_socket.bind((IP_ADDRESS, PORT))

    print(f"UDP server is listening on {IP_ADDRESS}:{PORT}")

    while True:
        # Receive data from the client
        # The UDP socket will wait here to receive data from the client in idle state
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        
        # Get the file name from the received data
        file_name = data.decode()

        # Construct the file path
        file_path = os.path.join(OBJECTS_DIR, file_name)

        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                # Send the file to the client chunk by chunk
                while True:
                    chunk = file.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    # print(chunk[-10:])
                    server_socket.sendto(chunk, client_address)

                print(f"Sent {file_name} to {client_address}")
        else:
            error_message = f"Error: File not found - {file_path}"
            server_socket.sendto(error_message.encode(), client_address)
            print(error_message)
            break  # Stop the server after handling one file


if __name__ == "__main__":
    udp_server()
