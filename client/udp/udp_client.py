import socket
import os

SERVER_IP = "192.168.1.8"      # Ganti dengan IP Ubuntu VM
SERVER_PORT = 9001

BUFFER_SIZE = 4096

TEMP_FOLDER = "static/temp"

os.makedirs(TEMP_FOLDER, exist_ok=True)


def request_video_stream(filename):

    filepath = os.path.join(TEMP_FOLDER, filename)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client.settimeout(5)

    try:

        # meminta video
        client.sendto(
            filename.encode(),
            (SERVER_IP, SERVER_PORT)
        )

        # menerima ukuran file
        data, _ = client.recvfrom(1024)

        if data == b"NOT_FOUND":
            print("Video tidak ditemukan di server.")
            return None

        filesize = int(data.decode())

        # kirim READY
        client.sendto(
            b"READY",
            (SERVER_IP, SERVER_PORT)
        )

        received = 0

        with open(filepath, "wb") as video:

            while True:

                packet, _ = client.recvfrom(65535)

                if packet == b"END_VIDEO":
                    break

                video.write(packet)

                received += len(packet)

                percent = (received / filesize) * 100

                print(f"\rDownloading : {percent:.2f}%", end="")

        print("\nVideo berhasil diterima.")

        return filepath

    except Exception as e:

        print(e)

        return None

    finally:

        client.close()