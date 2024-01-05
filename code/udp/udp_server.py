import socket
import os
import time
import hashlib
import sys

# Comment out next line if you wanna see prints for debug purpose
sys.stdout = open("/dev/null", "w")

IP_ADDRESS = "172.17.0.2"
PORT = 45404
OBJECTS_DIR = "/root/objects/"
EXPERIMENT_LOG_FILE = "server_experiment_log.txt"

WINDOW_SIZE = 100

BUFFER_SIZE = 2048
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

    # 4 bytes of sequence number
    # 16 bytes of checksum
    # The rest is data

    message = (
            f"{sequence_number:04}".encode() +
            checksum +
            data
    )
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
                # Sequence number is 4 bytes
                # MD5 checksum takes 16 bytes
                # The header length is 20 bytes, we subtract it from the buffer size
                # So that we read bytes from the file in the right amount
                chunk = file.read(BUFFER_SIZE - SEQUENCE_NUMBER_SIZE - CHECKSUM_SIZE)

                if not chunk:
                    # In case of the file finished, get out of the selective repeat moving window
                    break
                not_acked_counter = 0

                # We assign the sequence number to the data, so in case of data loss, we will use this
                # construction to resend the data again
                window[sequence_number] = chunk

                # We add sequence numbers to the sent_not_acked set, we will remove the ones which are acked from the set
                sent_not_acked.add(sequence_number)

                # Send the data
                send_data_with_reliability(
                    server_socket, sequence_number, chunk, client_address
                )

                # Increment the sequence number after sending the data
                sequence_number += 1

            # Receive acknowledgements from the client
            ack_numbers = receive_acknowledgments(server_socket, window)

            # remove ack numbers from the sent_not_acked set
            sent_not_acked.difference_update(ack_numbers)
            
            print("ack", ack_numbers)


            for ack in ack_numbers:
                if ack in acked_table:
                    # this is like an enum for duplicate ACKs
                    acked_table[ack] = 2
                else:
                    # this represents ACK which isn't duplicate
                    acked_table[ack] = 1

            for ack_number in ack_numbers:
                if ack_number not in window and acked_table[ack_number] > 1:
                    # If ACK is removed from the window but a duplicate ACK came from the client
                    # Discard the duplicate ACK
                    continue
                # Otherwise, remove the ACK'd packet from the window
                del window[ack_number]

            if not window and not chunk:
                # In case of window is cleared and the file is finished, leave the loop
                print("window chunk break")
                break

            for seq in sent_not_acked:
                if not_acked_counter <= 150:
                    # Sometimes client leaves and server has one last duplicate packet sending
                    # We covered this by giving a threshold which is reasonably high and more
                    # than the window size
                    print("resend", seq)
                    counter += 1

                    # In case of msg is not ACK'd after the timeout, we resend the messages
                    send_data_with_reliability(
                        server_socket, seq, window[seq], client_address
                    )
                    not_acked_counter += 1
                else:
                    return


def receive_acknowledgments(server_socket, window):
    ack_numbers = set()
    server_socket.settimeout(TIMEOUT)  # Set a timeout for receiving acknowledgments

    try:
        while True:
            # Sequence number is max 9999, so 4 bytes is enough
            # We fetch ACK number for 4 bytes, so we add each one separately
            data, _ = server_socket.recvfrom(SEQUENCE_NUMBER_SIZE)
            ack_numbers.add(int(data.decode()))

    except socket.timeout:
        # In case of timeout, the ack number isn't added to the set
        pass

    return ack_numbers


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # Initialize UDP socket
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the server socket to given IP address and the port number
        server_socket.bind((IP_ADDRESS, PORT))

        # Wait for the "ready" message from the client
        print("Waiting for the client to be ready...")
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        print(f"Received ready message from {client_address}")

        # We had a mixture of ready message and the ACKs, so we start sending after 100 ms
        time.sleep(0.1)

        # We start the timer after everything is ready
        start_time = time.time()

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

        # We write the timing results to our log file
        with open(EXPERIMENT_LOG_FILE, "a") as log_file:
            log_file.write(f"Experiment x: {elapsed_time} seconds\n")


if __name__ == "__main__":
    main()
