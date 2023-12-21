# echo-server.py

from pathlib import Path
import socket

HOST = "172.17.0.2"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            msg = conn.recv(10240)
            if not msg:
                break
            filename = msg.decode()
            path = filename
            with open(path, "rb") as f:
                data = f.read(10240)


            conn.sendall(data)