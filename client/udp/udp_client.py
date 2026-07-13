import socket
import os

SERVER_IP = "192.168.1.8"
SERVER_PORT = 9001

BUFFER_SIZE = 65535

TEMP_FOLDER = "static/temp"

os.makedirs(
    TEMP_FOLDER,
    exist_ok=True
)


def request_video_stream(filename):

    filepath = os.path.join(
        TEMP_FOLDER,
        filename
    )

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    client.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_RCVBUF,
        1024 * 1024
    )

    client.settimeout(20)

    try:

        client.sendto(
            filename.encode(),
            (SERVER_IP, SERVER_PORT)
        )

        data, _ = client.recvfrom(1024)

        if data == b"NOT_FOUND":

            print("Video tidak ditemukan.")

            return None

        filesize = int(data.decode())

        client.sendto(
            b"READY",
            (SERVER_IP, SERVER_PORT)
        )

        received = 0

        with open(filepath, "wb") as video:

            while received < filesize:

                packet, _ = client.recvfrom(BUFFER_SIZE)

                if packet == b"END_VIDEO":
                    break

                video.write(packet)

                received += len(packet)

                percent = received / filesize * 100

                print(
                    f"\rDownloading : {percent:.2f}%",
                    end=""
                )

        print("\nVideo berhasil diterima.")

        if received != filesize:

            print(
                f"Peringatan! File tidak lengkap ({received}/{filesize})"
            )

        return filepath

    except Exception as e:

        print(e)

        return None

    finally:

        client.close()