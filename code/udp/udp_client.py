import socket
import os

SERVER_IP_ADDRESS = "172.17.0.2"
SERVER_PORT = 45404
OBJECTS_DIR = "/root/objects/"

BUFFER_SIZE = 2048  # Adjust the buffer size according to your needs

def receive_and_save_objects(client_socket, objects_dir):
    # try:
        received_data = b""
        left, mid, right = b"", b"", b""

        for i in range(10):
            completed = False
            for size in "large", "small":
                received_data = right
                while True:
                    chunk, _ = client_socket.recvfrom(1024)
                    if not chunk:
                        print("break", size, i)
                        completed = True
                        break
                    left, mid, right = chunk.partition(b"=\n")
                    if not mid:
                        received_data += chunk
                    else:
                        received_data += left + mid
                        print(size,i,len(received_data))
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

    # except Exception as e:
    #     print(f"An error occurred: {e}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        # try:
            ready_message = b"Ready"
            client_socket.sendto(ready_message, (SERVER_IP_ADDRESS, SERVER_PORT))
            print("UDP Client is ready...")
            receive_and_save_objects(client_socket, OBJECTS_DIR)

        # except Exception as e:
        #     print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

# def udp_client(file_name):
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#     server_address = (IP_ADDRESS, PORT)
#
#     # Send the file name to the server
#     client_socket.sendto(file_name.encode(), server_address)
#
#     file_path = os.path.join(OBJECTS_DIR, file_name)
#
#     try:
#         with open(file_path, "wb") as file:
#             while True:
#                 chunk, _ = client_socket.recvfrom(BUFFER_SIZE)
#                 if not chunk:
#                     break
#                 if b"=" in chunk:
#                     file.write(chunk)
#                     break
#                 file.write(chunk)
#
#         print(f"Received and saved {file_name} to {file_path}")
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
#     finally:
#         client_socket.close()
#
#
# if __name__ == "__main__":
#     file_name = "small-1.obj"  # Specify the file to be requested
#     udp_client(file_name)
