import socket
import os

IP_ADDRESS = "172.17.0.2"
PORT = 12342
OBJECTS_DIR = "/app/udp/objects/"

def udp_client(file_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (IP_ADDRESS, PORT)

    # Send the file name to the server
    client_socket.sendto(file_name.encode(), server_address)

    # Receive the response from the server
    data, _ = client_socket.recvfrom(1024)

    try:
        file_path = os.path.join(OBJECTS_DIR, file_name)
        # Save the received data to a file
        with open(file_path, "wb") as file:
            file.write(data)
        print(f"Received {file_name} from {server_address}")
    except IOError as e:
        print(f"Error saving file {file_name}: {e}")


if __name__ == "__main__":
    file_name = "small-0.obj"  # Specify the file to be requested
    udp_client(file_name)
