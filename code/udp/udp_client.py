import hashlib
import socket
import os
import sys

SERVER_IP_ADDRESS = "172.17.0.2"
SERVER_PORT = 45404
OBJECTS_DIR = "/root/objects/"

WINDOW_SIZE = 100

BUFFER_SIZE = 2048
SEQUENCE_NUMBER_SIZE = 4
CHECKSUM_SIZE = 16

# Comment out next line if you wanna see prints for debug purpose
sys.stdout = open("/dev/null", "w")


corrupted_count = 0


def calculate_checksum(data):
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.digest()


def send_acknowledgment(client_socket, ack_number):
    client_socket.sendto(f"{ack_number:04}".encode(), (SERVER_IP_ADDRESS, SERVER_PORT))


def receive_and_save_objects(client_socket, objects_dir):

    # We have a window of received objects
    received_dict = {}

    global corrupted_count

    while True:
        # Message comes from the buffer and header and data is separated by fixed sizes
        message, _ = client_socket.recvfrom(BUFFER_SIZE)
        sequence_number = int(message[:SEQUENCE_NUMBER_SIZE])
        checksum = message[SEQUENCE_NUMBER_SIZE : SEQUENCE_NUMBER_SIZE + CHECKSUM_SIZE]
        chunk = message[SEQUENCE_NUMBER_SIZE + CHECKSUM_SIZE :]

        # We compare the packets' checksum and if they are not equal
        # Server needs the resend the packet because of no ACK
        client_checksum = calculate_checksum(chunk)

        if not client_checksum == checksum:
            print("corrupted", sequence_number)
            corrupted_count += 1
            continue

        print("receive", sequence_number, len(chunk))
        if sequence_number not in received_dict:
            # In case of non-duplicate sequence, we update the received sequence
            # This is also for tagging and sorting purposes
            # At the end, packets will be in correct order
            received_dict[sequence_number] = chunk
        else:
            # Otherwise it means it's duplicate
            print("duplicate", sequence_number)
        send_acknowledgment(client_socket, sequence_number)

        print(len(received_dict), int(sequence_number) + 1)

        if b"".join(received_dict.values()).count(b"=\n") == 20:
            # We found out that the files are ending with = and new line
            # If we have 20 of them this means we transfered all objects
            # But there is an edge case which is that the last part of object came faster
            # than previous sequences. The one having the last = must have the highest sequence
            # number so we use this information so that when our dict has a length one higher than
            # the max_key (because seq num starts from 0, that makes sense)
            # We are ready to break the loop
            max_key = max(received_dict.keys())
            print(len(received_dict), int(sequence_number) + 1)
            # print(sorted(received_dict.keys()))
            if len(received_dict) == int(max_key) + 1:
                print("break")  # , size, i)
                completed = True
                break

    # And finally we sort the key according to their tags, so that the data is in correct order
    received_data = b"".join(received_dict[key] for key in sorted(received_dict.keys()))
    print(len(received_data))

    # We separate each file accourding to their endings
    file_datas = [file + b"=\n" for file in received_data.split(b"=\n")][:-1]

    for idx, file_data in enumerate(file_datas):
        # This is a trick which we determine the object number and whether it's small or large
        file_idx, size_idx = divmod(idx, 2)
        size = "small" if size_idx else "large"

        # The rest covers the writing the file to the client's docker
        # We checked the file checksums with linux's md5sum command and they work
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
        # Client initiates the first message so that server starts sending
        ready_message = b"Ready"
        client_socket.sendto(ready_message, (SERVER_IP_ADDRESS, SERVER_PORT))
        print("UDP Client is ready...")
        receive_and_save_objects(client_socket, OBJECTS_DIR)

        print("corrupted", corrupted_count)


if __name__ == "__main__":
    main()
