import socket
import os
import time

IP_ADDRESS = "172.17.0.2"
PORT = 45404
OBJECTS_DIR = "/root/objects/"
EXPERIMENT_LOG_FILE = "server_experiment_log.txt"

WINDOW_SIZE = 5

BUFFER_SIZE = 1024  # Adjust the buffer size according to your needs
HEADER_SIZE = 4
HEADER_SEPARATOR = ":"
TIMEOUT = 0.1

def send_data_with_reliability(server_socket, sequence_number, data, client_address):
    print("send", sequence_number, len(data))
    server_socket.sendto(f"{sequence_number:04}{HEADER_SEPARATOR}{data.decode()}".encode(), client_address)


def send_file(server_socket, file_path, client_address):
    with open(file_path, "rb") as file:
        sequence_number = 0
        window = {}
        sent_not_acked = set()

        while True:
            while len(window) < WINDOW_SIZE:
                chunk = file.read(BUFFER_SIZE - HEADER_SIZE)
                time.sleep(0.001)
                if not chunk:
                    break
                window[sequence_number] = chunk
                sent_not_acked.add(sequence_number)
                sequence_number += 1
                send_data_with_reliability(server_socket, sequence_number, chunk, client_address)
                # server_socket.sendto(f"{sequence_number:04}{HEADER_SEPARATOR}{chunk.decode()}".encode(), client_address)

            ack_numbers = receive_acknowledgments(server_socket, window)
            sent_not_acked.difference_update(ack_numbers)

            for ack_number in ack_numbers:
                del window[ack_number - 1]

            if not window and not chunk:
                break

            for seq in sent_not_acked:
                send_data_with_reliability(server_socket, seq, window[seq], client_address)

            time.sleep(TIMEOUT)

def receive_acknowledgments(server_socket, window):
    ack_numbers = set()
    server_socket.settimeout(TIMEOUT)  # Set a timeout for receiving acknowledgments

    try:
        while True:
            data, _ = server_socket.recvfrom(HEADER_SIZE)
            ack_numbers.add(int(data.decode()))

    except socket.timeout:
        pass

    return ack_numbers


def main():
    # try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((IP_ADDRESS, PORT))

            # Wait for the "ready" message from the client
            print("Waiting for the client to be ready...")
            data, client_address = server_socket.recvfrom(1024)
            print(f"Received ready message from {client_address}")

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
            with open(EXPERIMENT_LOG_FILE, "a") as log_file:
                log_file.write(f"Experiment x: {elapsed_time} seconds\n")

    # except Exception as e:
    #     print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()


# def udp_server():
#     # Create a UDP socket
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#     # Set the socket options to allow quick reuse of the socket
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
#
#     # Bind the socket to the IP address and port
#     server_socket.bind((IP_ADDRESS, PORT))
#
#     print(f"UDP server is listening on {IP_ADDRESS}:{PORT}")
#
#     while True:
#         # Receive data from the client
#         # The UDP socket will wait here to receive data from the client in idle state
#         data, client_address = server_socket.recvfrom(BUFFER_SIZE)
#
#         # Get the file name from the received data
#         file_name = data.decode()
#
#         # Construct the file path
#         file_path = os.path.join(OBJECTS_DIR, file_name)
#
#         if os.path.exists(file_path):
#             with open(file_path, "rb") as file:
#                 # Send the file to the client chunk by chunk
#                 while True:
#                     chunk = file.read(BUFFER_SIZE)
#                     if not chunk:
#                         break
#                     # print(chunk[-10:])
#                     server_socket.sendto(chunk, client_address)
#
#                 print(f"Sent {file_name} to {client_address}")
#         else:
#             error_message = f"Error: File not found - {file_path}"
#             server_socket.sendto(error_message.encode(), client_address)
#             print(error_message)
#             break  # Stop the server after handling one file
#
#
# if __name__ == "__main__":
#     udp_server()
