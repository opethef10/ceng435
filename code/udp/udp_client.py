import hashlib
import socket
import os
import sys

SERVER_IP_ADDRESS = "172.17.0.2"
SERVER_PORT = 45404
OBJECTS_DIR = "/app/udp/objects/"

WINDOW_SIZE = 100

BUFFER_SIZE = 2048  # Adjust the buffer size according to your needs
SEQUENCE_NUMBER_SIZE = 4
CHECKSUM_SIZE = 16



sys.stdout = open("/dev/null", "w")


corrupted_count = 0


def calculate_checksum(data):
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.digest()


def send_acknowledgment(client_socket, ack_number):
    client_socket.sendto(f"{ack_number:04}".encode(), (SERVER_IP_ADDRESS, SERVER_PORT))


def receive_and_save_objects(client_socket, objects_dir):
    # try:
    received_data = b""
    left, mid, right = b"", b"", b""
    received_dict = {}

    global corrupted_count

    while True:
        message, _ = client_socket.recvfrom(BUFFER_SIZE)
        sequence_number = int(message[:SEQUENCE_NUMBER_SIZE])
        checksum = message[SEQUENCE_NUMBER_SIZE : SEQUENCE_NUMBER_SIZE + CHECKSUM_SIZE]
        chunk = message[SEQUENCE_NUMBER_SIZE + CHECKSUM_SIZE :]
        # sequence_number, chunk, checksum = message.split(HEADER_SEPARATOR.encode())

        client_checksum = calculate_checksum(chunk)

        if not client_checksum == checksum:
            print("corrupted", sequence_number)
            corrupted_count += 1
            continue

        # sequence_number = sequence_number.decode()
        # chunk = chunk.encode()
        print("receive", sequence_number, len(chunk))
        if sequence_number not in received_dict:
            received_dict[sequence_number] = chunk
        else:
            print("duplicate", sequence_number)
        send_acknowledgment(client_socket, sequence_number)

        print(len(received_dict), int(sequence_number) + 1)

        if b"".join(received_dict.values()).count(b"=\n") == 20:
            max_key = max(received_dict.keys())
            print(len(received_dict), int(sequence_number) + 1)
            # print(sorted(received_dict.keys()))
            if len(received_dict) == int(max_key) + 1:
                print("break")  # , size, i)
                completed = True
                break

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


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        # try:
        ready_message = b"Ready"
        client_socket.sendto(ready_message, (SERVER_IP_ADDRESS, SERVER_PORT))
        print("UDP Client is ready...")
        receive_and_save_objects(client_socket, OBJECTS_DIR)

        print("corrupted", corrupted_count)


if __name__ == "__main__":
    main()
