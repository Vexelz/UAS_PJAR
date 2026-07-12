import socket
import struct
import os

SERVER_IP = "192.168.1.8"
SERVER_PORT = 9000


def upload_file(file):

    filename = os.path.basename(file.filename)

    file.seek(0, os.SEEK_END)
    filesize = file.tell()
    file.seek(0)

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((SERVER_IP, SERVER_PORT))

    filename_bytes = filename.encode()

    client.sendall(
        struct.pack("!I", len(filename_bytes))
    )

    client.sendall(filename_bytes)

    client.sendall(
        struct.pack("!Q", filesize)
    )

    while True:

        data = file.read(4096)

        if not data:
            break

        client.sendall(data)

    response = client.recv(1024).decode()

    client.close()

    return response