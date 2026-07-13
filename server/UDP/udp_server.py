import socket
import os
import time

HOST = "0.0.0.0"
PORT = 9001

BUFFER_SIZE = 60000

VIDEO_FOLDER = "../tcp/received_files"

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_SNDBUF,
    1024 * 1024
)

server.bind((HOST, PORT))

print(f"UDP Server berjalan di {HOST}:{PORT}")

while True:

    data, address = server.recvfrom(1024)

    filename = data.decode()

    filepath = os.path.join(
        VIDEO_FOLDER,
        filename
    )

    print(f"\nRequest video : {filename}")

    if not os.path.exists(filepath):

        server.sendto(
            b"NOT_FOUND",
            address
        )

        print("File tidak ditemukan.")

        continue

    filesize = os.path.getsize(filepath)

    server.sendto(
        str(filesize).encode(),
        address
    )

    ack, _ = server.recvfrom(1024)

    if ack != b"READY":
        continue

    print("Mulai streaming...")

    with open(filepath, "rb") as video:

        sent = 0

        while True:

            chunk = video.read(BUFFER_SIZE)

            if not chunk:
                break

            server.sendto(
                chunk,
                address
            )

            sent += len(chunk)

            percent = sent / filesize * 100

            print(
                f"\rStreaming : {percent:.2f}%",
                end=""
            )

            # supaya client tidak kebanjiran paket
            time.sleep(0.002)

    server.sendto(
        b"END_VIDEO",
        address
    )

    print("\nStreaming selesai.")