import socket
import os

IP_ADDRESS = "172.17.0.2"
PORT = 12343
OBJECTS_DIR = "/app/tcp/objects/"


def receive_and_save_objects(client_socket, objects_dir):
    try:
        received_data = b""
        left, mid, right = b"", b"", b""

        for i in range(10):
            completed = False
            for size in "large", "small":
                received_data = right
                while True:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        completed = True
                        break
                    left, mid, right = chunk.partition(b"=\n")
                    if not mid:
                        received_data += chunk
                    else:
                        received_data += left + mid
                        break

                if not os.path.exists(objects_dir):
                    os.makedirs(objects_dir)

                file_path = os.path.join(objects_dir, f"received_{size}-{i}.obj")

                try:
                    with open(file_path, "wb") as file:
                        file.write(received_data)
                    print(f"Received and saved {size} Object {i} to {file_path}")

                except Exception as e:
                    print(f"Error saving {size} Object {i}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((IP_ADDRESS, PORT))
            print("Connected to the server...")
            receive_and_save_objects(client_socket, OBJECTS_DIR)

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
