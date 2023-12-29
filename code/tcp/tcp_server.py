import socket
import os
import time

IP_ADDRESS = "172.17.0.2"
PORT = 12343
OBJECTS_DIR = "/root/objects/"
EXPERIMENT_LOG_FILE = "server_experiment_log.txt"


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((IP_ADDRESS, PORT))
            server_socket.listen(1)
            print("Server is listening for incoming connections...")

            start_time = time.time()

            connection, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            for i in range(10):
                for size in "large", "small":
                    file_path = os.path.join(OBJECTS_DIR, f"{size}-{i}.obj")

                    if not os.path.exists(file_path):
                        print(f"Error: File not found - {file_path}")
                        continue

                    with open(file_path, "rb") as file:
                        data = file.read()

                    connection.sendall(data)
                    print(f"Sent {size} Object {i}")

            end_time = time.time()
            elapsed_time = end_time - start_time
            with open(EXPERIMENT_LOG_FILE, "a") as log_file:
                log_file.write(f"Experiment x: {elapsed_time} seconds\n")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
