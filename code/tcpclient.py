# echo-client.py
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip_addr = "172.17.0.2"
port_num = 12345

client.connect((ip_addr, port_num))

data = "Server test! 1 2 3"

try:
    client.sendall(data.encode())

    # get response
    response = client.recv(1024)
    print(f"Response: {response.decode()} from server {ip_addr}")

finally:
    client.close()
