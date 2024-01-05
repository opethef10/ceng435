import hashlib
import socket
import os

SERVER_IP_ADDRESS = "172.17.0.2"
SERVER_PORT = 45404
OBJECTS_DIR = "/app/udp/objects/"

WINDOW_SIZE = 5

BUFFER_SIZE = 1024  # Adjust the buffer size according to your needs
SEQUENCE_NUMBER_SIZE = 4
CHECKSUM_SIZE = 16
HEADER_SEPARATOR = ":"


def calculate_checksum(data):
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.digest()


def receive_data_with_reliability(client_socket, expected_sequence_number):
    while True:
        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        sequence_number, chunk = data.decode().split(HEADER_SEPARATOR)

        if int(sequence_number) == expected_sequence_number:
            return chunk, expected_sequence_number
        else:
            print(
                f"Received out-of-order packet. Expected: {expected_sequence_number}, Received: {sequence_number}"
            )


def receive_file(client_socket):
    expected_sequence_number = 0

    while True:
        chunk, sequence_number = receive_data_with_reliability(
            client_socket, expected_sequence_number
        )

        with open(OBJECTS_DIR + f"received_{sequence_number}.obj", "ab") as file:
            file.write(chunk)

        expected_sequence_number += 1


def send_acknowledgment(client_socket, ack_number):
    client_socket.sendto(f"{ack_number:04}".encode(), (SERVER_IP_ADDRESS, SERVER_PORT))


def receive_and_save_objects(client_socket, objects_dir):
    # try:
    received_data = b""
    left, mid, right = b"", b"", b""
    received_dict = {}

    while True:
        message, _ = client_socket.recvfrom(1024)
        print(message)
        sequence_number = int(message[:SEQUENCE_NUMBER_SIZE])
        checksum = message[SEQUENCE_NUMBER_SIZE: SEQUENCE_NUMBER_SIZE + CHECKSUM_SIZE]
        chunk = message[SEQUENCE_NUMBER_SIZE + CHECKSUM_SIZE:]
        # sequence_number, chunk, checksum = message.split(HEADER_SEPARATOR.encode())
        
        
        # sequence_number = sequence_number.decode()
        # chunk = chunk.encode()
        print("receive", sequence_number, len(chunk))
        if sequence_number not in received_dict:
            received_dict[sequence_number] = chunk
        else:
            print("duplicate", sequence_number)
        send_acknowledgment(client_socket, sequence_number)

        print(len(received_dict), int(sequence_number) + 1)

        if b"".join(received_dict.values()).count(b"=\n") == 2:
            print(len(received_dict), int(sequence_number) + 1)
            if len(received_dict) == int(sequence_number) + 1:
                print("break")  # , size, i)
                completed = True
                break
        # received_data += chunk
        # # continue
        # if received_data.count(b"=\n") == 20: #20

    received_data = b"".join(received_dict[key] for key in sorted(received_dict.keys()))
    print(len(received_data))

    file_datas = [file + b"=\n" for file in received_data.split(b"=\n")][:-1]

    for idx, file_data in enumerate(file_datas):
        file_idx, size_idx = divmod(idx, 2)
        size = "small" if size_idx else "large"

        if not os.path.exists(objects_dir):
            os.makedirs(objects_dir)

        file_path = os.path.join(objects_dir, f"received_{size}-{file_idx}.obj")

        try:
            with open(file_path, "wb") as file:
                file.write(file_data)
            print(f"Received and saved {size} Object {file_idx} to {file_path}")

        except Exception as e:
            print(f"Error saving {size} Object {file_idx}: {e}")

        # left, mid, right = chunk.partition(b"=\n")
        # if not mid:
        #     received_data += chunk
        # else:
        #     received_data += left + mid
        #     print(size, i, len(received_data))
        #     break

    # for i in range(10):
    #     completed = False
    #     for size in "large", "small":
    #         received_data = right
    #         while True:
    #             chunk, _ = client_socket.recvfrom(1024)
    #             sequence_number, chunk = chunk.decode().split(HEADER_SEPARATOR)
    #             chunk = chunk.encode()
    #             print("receive", sequence_number, len(chunk))
    #             send_acknowledgment(client_socket, sequence_number)
    #             # continue
    #             if not chunk:
    #                 print("break", size, i)
    #                 completed = True
    #                 break
    #             left, mid, right = chunk.partition(b"=\n")
    #             if not mid:
    #                 received_data += chunk
    #             else:
    #                 received_data += left + mid
    #                 print(size,i,len(received_data))
    #                 break
    #
    #         if not os.path.exists(objects_dir):
    #             os.makedirs(objects_dir)
    #
    #         file_path = os.path.join(objects_dir, f"received_{size}-{i}.obj")
    #
    #         try:
    #             with open(file_path, "wb") as file:
    #                 file.write(received_data)
    #             print(f"Received and saved {size} Object {i} to {file_path}")
    #
    #         except Exception as e:
    #             print(f"Error saving {size} Object {i}: {e}")


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
