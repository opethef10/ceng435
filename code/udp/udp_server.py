import socket
import os
import time
import hashlib
import sys

sys.stdout = open("/dev/null", "w")

IP_ADDRESS = "172.17.0.2"
PORT = 45404
OBJECTS_DIR = "/root/objects/"
EXPERIMENT_LOG_FILE = "server_experiment_log.txt"

# IP_ADDRESS = "0.0.0.0"
# PORT = 45404
# OBJECTS_DIR = "../../objects/"



WINDOW_SIZE = 100

BUFFER_SIZE = 2048  # Adjust the buffer size according to your needs
CHECKSUM_SIZE = 16
SEQUENCE_NUMBER_SIZE = 4
TIMEOUT = 0.15


def calculate_checksum(data):
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.digest()

def send_data_with_reliability(server_socket, sequence_number, data, client_address):
    print("send", sequence_number, len(data))
    checksum = calculate_checksum(data)
    message = (
            f"{sequence_number:04}".encode() +
            # HEADER_SEPARATOR.encode() +
            checksum +
            data
            # HEADER_SEPARATOR.encode() +
            # checksum
    )
    # f"{sequence_number:04}{HEADER_SEPARATOR}{data.decode()}".encode()
    server_socket.sendto(
        message,
        client_address,
    )


sequence_number = 0
window = {}
sent_not_acked = set()
ack_list = []
acked_table = {}
counter = 0


def send_file(server_socket, file_path, client_address):
    with open(file_path, "rb") as file:
        global sequence_number
        global counter
        not_acked_counter = 0
        chunk = b''
        while True:
            while len(window) < WINDOW_SIZE:
                chunk = file.read(BUFFER_SIZE - SEQUENCE_NUMBER_SIZE - CHECKSUM_SIZE)
                # time.sleep(0.001)
                if not chunk:
                    break
                not_acked_counter = 0
                window[sequence_number] = chunk
                sent_not_acked.add(sequence_number)
                send_data_with_reliability(
                    server_socket, sequence_number, chunk, client_address
                )
                sequence_number += 1

            ack_numbers = receive_acknowledgments(server_socket, window)
            sent_not_acked.difference_update(ack_numbers)
            
            print("ack", ack_numbers)


            for ack in ack_numbers:
                if (ack) in acked_table:
                    acked_table[(ack)] = 2
                else:
                    acked_table[(ack)] = 1

            for ack_number in ack_numbers:
                # if ack_number not in window and ack_number in filtered_list:
                #     continue
                if ack_number not in window and acked_table[(ack_number)] > 1:
                    continue
                del window[ack_number]
                # if ack_number not in window and ack_number in acked_table:
                #     continue

            if not window and not chunk:
                print("window chunk break")
                break

            for seq in sent_not_acked:
                if not_acked_counter <= 150:
                    print("resend", seq)
                    counter += 1
                    send_data_with_reliability(
                        server_socket, seq, window[seq], client_address
                    )
                    not_acked_counter += 1
                else:
                    return

            # time.sleep(TIMEOUT)


def receive_acknowledgments(server_socket, window):
    ack_numbers = set()
    server_socket.settimeout(TIMEOUT)  # Set a timeout for receiving acknowledgments

    try:
        while True:
            data, _ = server_socket.recvfrom(SEQUENCE_NUMBER_SIZE)
            ack_numbers.add(int(data.decode()))

    except socket.timeout:
        pass

    return ack_numbers


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((IP_ADDRESS, PORT))

        # Wait for the "ready" message from the client
        print("Waiting for the client to be ready...")
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        print(f"Received ready message from {client_address}")
        
        time.sleep(0.1)

        start_time = time.time()

        # connection, client_address = server_socket.accept()
        # print(f"Connection from {client_address}")

        for i in range(10):
            for size in "large", "small":
                file_path = os.path.join(OBJECTS_DIR, f"{size}-{i}.obj")

                if not os.path.exists(file_path):
                    print(f"Error: File not found - {file_path}")
                    continue
                send_file(server_socket, file_path, client_address)
                print(f"Sent {size} Object {i}")

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Counter: {counter}")
        with open(EXPERIMENT_LOG_FILE, "a") as log_file:
            log_file.write(f"Experiment x: {elapsed_time} seconds\n")




if __name__ == "__main__":
    main()
