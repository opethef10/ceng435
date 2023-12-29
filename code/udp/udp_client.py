import socket
import os

IP_ADDRESS = "0.0.0.0"
PORT = 45404
OBJECTS_DIR = "./test_obj/"

BUFFER_SIZE = 2048  # Adjust the buffer size according to your needs


def udp_client(file_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (IP_ADDRESS, PORT)

    # Send the file name to the server
    client_socket.sendto(file_name.encode(), server_address)

    file_path = os.path.join(OBJECTS_DIR, file_name)

    try:
        with open(file_path, "wb") as file:
            while True:
                chunk, _ = client_socket.recvfrom(BUFFER_SIZE)
                if not chunk:
                    break
                if b"=" in chunk:
                    file.write(chunk)
                    break
                file.write(chunk)

        print(f"Received and saved {file_name} to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    file_name = "small-1.obj"  # Specify the file to be requested
    udp_client(file_name)
