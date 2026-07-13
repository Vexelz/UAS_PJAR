import socket
import struct
import os

HOST = "0.0.0.0"
PORT = 9000

SAVE_FOLDER = "received_files"

os.makedirs(SAVE_FOLDER, exist_ok=True)


def recv_all(sock, length):

    data = b""

    while len(data) < length:

        packet = sock.recv(length - len(data))

        if not packet:
            return None

        data += packet

    return data


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen(5)

print("=" * 40)
print(" TCP FILE SERVER BERJALAN ")
print(f" HOST : {HOST}")
print(f" PORT : {PORT}")
print("=" * 40)


while True:

    client, address = server.accept()

    print(f"\nClient Terhubung : {address}")

    try:

        # -------------------------
        # Panjang nama file (4 byte)
        # -------------------------

        filename_length_data = recv_all(client, 4)

        if filename_length_data is None:
            raise Exception("Gagal menerima panjang nama file.")

        filename_length = struct.unpack(
            "!I",
            filename_length_data
        )[0]

        # -------------------------
        # Nama File
        # -------------------------

        filename_data = recv_all(
            client,
            filename_length
        )

        if filename_data is None:
            raise Exception("Gagal menerima nama file.")

        filename = filename_data.decode()

        # -------------------------
        # Ukuran File (8 byte)
        # -------------------------

        filesize_data = recv_all(client, 8)

        if filesize_data is None:
            raise Exception("Gagal menerima ukuran file.")

        filesize = struct.unpack(
            "!Q",
            filesize_data
        )[0]

        print(f"Nama File : {filename}")
        print(f"Ukuran    : {filesize} Bytes")

        filepath = os.path.join(
            SAVE_FOLDER,
            filename
        )

        received = 0

        with open(filepath, "wb") as file:

            while received < filesize:

                data = client.recv(4096)

                if not data:
                    break

                file.write(data)

                received += len(data)

                percent = (received / filesize) * 100

                print(
                    f"\rMenerima : {percent:.2f}%",
                    end=""
                )

        print()

        # -------------------------
        # Validasi hasil upload
        # -------------------------

        if received == filesize:

            print("Upload Berhasil!")
            print(f"Disimpan di : {filepath}")

            client.sendall(b"SUCCESS")

        else:

            print("Upload Gagal!")
            print(f"Diterima {received} dari {filesize} byte.")

            if os.path.exists(filepath):
                os.remove(filepath)

            client.sendall(b"FAILED")

    except Exception as e:

        print("\nTerjadi Error :", e)

        try:
            client.sendall(b"FAILED")
        except:
            pass

    finally:

        client.close()