# Portal Pengiriman dan Streaming Media

Deskripsi singkat: Aplikasi web untuk pendaftaran pengguna, verifikasi email, login dengan OTP, pengiriman file (upload) menggunakan protokol TCP, dan pemutaran/streaming video menggunakan protokol UDP. Aplikasi terdiri dari bagian client (Flask) yang menjalankan antarmuka web dan utilitas jaringan, serta server terpisah untuk menerima file (TCP) dan mengirimkan aliran video (UDP).

## Fitur

- Registrasi akun dengan form pendaftaran (`/register`).
- Verifikasi email setelah pendaftaran melalui link berisi token verifikasi.
- Login menggunakan email dan password; setelah login dikirimkan kode OTP lewat email.
- Pengecekan OTP untuk menyelesaikan proses login.
- Halaman dashboard sederhana untuk pengguna yang sudah login.
- Upload file (video/media) dari client ke TCP Server menggunakan koneksi TCP (binary transfer).
- Permintaan streaming video dari client ke UDP Server; file diterima dan disimpan sementara di folder `client/static/temp` sebelum ditampilkan.
- Logout untuk menghapus sesi pengguna.

## Teknologi yang Digunakan

- Bahasa pemrograman: Python 3
- Web framework: Flask
- Template: Jinja2 (via Flask)
- Database: SQLite (file `client/database/users.db`)
- SMTP (library standar `smtplib` dan `email.mime`) untuk pengiriman email verifikasi dan OTP
- Manajemen konfigurasi: python-dotenv (`dotenv`) untuk membaca file `.env`
- Modul jaringan: `socket`, `struct` (modul standar Python) untuk komunikasi TCP/udp dan pengiriman data biner
- Protokol jaringan: TCP (untuk upload file) dan UDP (untuk streaming video)
- Library bantu: modul standar lain yang digunakan di kode (os, secrets, random, datetime, time)

Catatan: daftar paket terdaftar pada `client/requirements.txt` untuk instalasi lingkungan Flask.

## Arsitektur Aplikasi

Arsitektur terdiri dari dua bagian utama:

- Client (Flask): Menyediakan antarmuka web (form register, login, otp, dashboard, upload, streaming). Client juga bertanggung jawab untuk:
	- Menyimpan dan membaca konfigurasi dari `.env` (mis. pengaturan SMTP, `BASE_URL`).
	- Mengirim email verifikasi dan OTP menggunakan SMTP.
	- Mengirim file ke TCP Server dengan modul socket (fungsi `upload_file` di `client/tcp/tcp_client.py`).
	- Meminta streaming video dari UDP Server (fungsi `request_video_stream` di `client/udp/udp_client.py`) yang menulis berkas sementara di `client/static/temp`.

- Server TCP: Menjalankan `server/tcp/tcp_server.py`. Menerima koneksi TCP, membaca nama file dan ukuran (format biner menggunakan `struct`), menerima isi file dan menyimpannya ke `server/tcp/received_files`.

- Server UDP: Menjalankan `server/udp/udp_server.py`. Menerima permintaan nama file via UDP, mengirim ukuran file, menunggu konfirmasi `READY`, lalu mengirim data file berukuran chunk sampai selesai, diakhiri paket `END_VIDEO`.

- Database SQLite: `client/database/users.db` menyimpan tabel `users` yang berisi data akun, token verifikasi, dan OTP.

Hubungan singkat: pengguna mendaftar di antarmuka Flask → server mengirim email verifikasi (SMTP) → setelah verifikasi, pengguna dapat login → server Flask mengirim OTP lewat email → setelah validasi OTP, pengguna dapat mengunggah file ke TCP Server → file disimpan di server TCP → untuk streaming, client meminta file lewat UDP Server yang membaca file di lokasi hasil upload dan mengirimkan datanya ke client.

## Struktur Folder

- `client/` : Kode aplikasi web (Flask) dan utilitas client.
	- `app.py` : Entrypoint Flask yang menangani rute (login, register, otp, upload, streaming, verify, dashboard, logout).
	- `config.py` : Pembacaan variabel konfigurasi dari `.env`.
	- `.env .example` : Contoh variabel lingkungan (SECRET_KEY, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, BASE_URL).
	- `requirements.txt` : Daftar paket Python yang direkomendasikan.
	- `auth/send_email.py` : Fungsi pengiriman email verifikasi dan OTP (menggunakan `smtplib`).
	- `database/database.py` : Inisialisasi database SQLite dan fungsi-fungsi terkait (`register`, `login`, `create_verify_token`, `verify_token`, `create_otp`, `verify_otp`, `get_user_by_email`).
	- `tcp/tcp_client.py` : Fungsi `upload_file` untuk mengirim file ke TCP Server.
	- `udp/udp_client.py` : Fungsi `request_video_stream` untuk meminta dan menerima streaming video via UDP.
	- `templates/` : Folder template HTML Jinja2 (login, register, otp, dashboard, upload, streaming, verifikasi, dsb.).
	- `static/temp/` : Folder sementara untuk menyimpan video yang diterima dari UDP sebelum ditampilkan.
	- `uploads_temp/` : (folder ada di repo sebagai lokasi sementara untuk upload, digunakan oleh aplikasi jika diperlukan)

- `server/`
	- `TCP/tcp_server.py` : Server TCP yang menerima file dan menyimpannya ke `server/tcp/received_files`.
	- `UDP/udp_server.py` : Server UDP yang mengirim file video ke client atas permintaan.

## Cara Menjalankan Project

Pastikan Python 3.8+ terpasang pada sistem. Contoh perintah di Windows (PowerShell) atau terminal lainnya:

1. Buat virtual environment dan aktifkan (opsional tapi disarankan):

```bash
cd client
python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Windows (cmd)
venv\Scripts\activate.bat
# macOS / Linux
# source venv/bin/activate
```

2. Install dependency:

```bash
pip install -r requirements.txt
# Jika belum terpasang, pasang python-dotenv:
pip install python-dotenv
```

3. Konfigurasi environment:

- Salin `client/.env .example` menjadi `client/.env` dan isi nilai `MAIL_USERNAME`, `MAIL_PASSWORD`, `SECRET_KEY` dan `BASE_URL` sesuai kebutuhan.

4. Jalankan TCP Server (penerima file):

```bash
# Jalankan dari root workspace
python server/tcp/tcp_server.py
```

5. Jalankan UDP Server (streaming):

```bash
python server/udp/udp_server.py
```

6. Jalankan aplikasi Flask (client web):

```bash
cd client
python app.py
```

Catatan penting:
- Pastikan alamat `SERVER_IP` di `client/tcp/tcp_client.py` dan `client/udp/udp_client.py` mengarah ke IP server tempat `tcp_server.py` dan `udp_server.py` dijalankan (default di kode: `192.168.1.8`). Jika semua dijalankan pada mesin yang sama, set ke `127.0.0.1` atau `localhost`.
- Jika menggunakan Gmail untuk pengiriman email, Anda harus menggunakan App Password (jika otentikasi 2FA aktif) atau menyesuaikan konfigurasi SMTP sesuai penyedia email.

## Menjalankan Server pada Ubuntu Server (VM)

Petunjuk singkat berikut menjelaskan langkah menjalankan server TCP dan UDP pada mesin Ubuntu (mis. VM). Sesuaikan nama pengguna, alamat IP, dan jalur folder proyek dengan lingkungan Anda.

### 1. Login ke Ubuntu Server melalui SSH

```bash
ssh izza@192.168.1.8
```

### 2. Masuk ke folder project

```bash
cd ~/ujian_pjar
```

### 3. Menjalankan TCP Server

```bash
cd server/tcp
python3 tcp_server.py
```

atau

```bash
python3 ~/ujian_pjar/server/tcp/tcp_server.py
```

### 4. Membuka terminal SSH kedua

Login kembali menggunakan SSH.

```bash
ssh name@192.-.-.-
```

### 5. Menjalankan UDP Server

```bash
cd ~/ujian_pjar/server/udp
python3 udp_server.py
```

atau

```bash
python3 ~/ujian_pjar/server/udp/udp_server.py
```

### 6. Menjalankan kedua server dalam satu terminal (opsional)

```bash
python3 ~/ujian_pjar/server/tcp/tcp_server.py &
python3 ~/ujian_pjar/server/udp/udp_server.py
```

- TCP Server digunakan untuk menerima upload file video.
- UDP Server digunakan untuk mengirim video saat proses streaming.
- Kedua server harus berjalan bersamaan agar seluruh fitur aplikasi dapat digunakan.

## Cara Menggunakan Aplikasi

1. Registrasi akun
	 - Buka alamat `http://127.0.0.1:5000/register`.
	 - Isi nama pengguna, email, dan password. Setelah submit, aplikasi akan membuat token verifikasi dan mengirim email verifikasi.

2. Verifikasi email
	 - Buka link yang dikirim ke email. Link mengarah ke rute `/verify/<token>` di aplikasi Flask.
	 - Token berlaku selama 5 menit (sesuai implementasi di `database/database.py`).

3. Login
	 - Setelah akun terverifikasi, buka halaman login `http://127.0.0.1:5000/`.
	 - Masukkan email dan password.

4. OTP Email
	 - Setelah memasukkan kredensial yang benar, server membuat OTP 6 digit dan mengirimkannya ke email pengguna.
	 - Buka halaman `/otp` dan masukkan kode OTP yang diterima. OTP berlaku selama 5 menit.

5. Dashboard
	 - Setelah OTP valid, pengguna dialihkan ke halaman dashboard.

6. Upload video menggunakan TCP
	 - Pada halaman `Upload`, pilih file lalu submit.
	 - Client akan membuka koneksi TCP ke `SERVER_IP:9000`, mengirim nama file (dengan panjang nama sebagai 4 byte), ukuran file (8 byte, unsigned long long), lalu isi file dalam blok 4096 byte.
	 - Server TCP menyimpan file ke `server/tcp/received_files`.

7. Streaming video menggunakan UDP
	 - Pada halaman `Streaming`, client mengirim permintaan nama file via UDP ke `SERVER_IP:9001`.
	 - Server UDP akan mengirim ukuran file, client mengirim `READY`, lalu server mengirim chunk data sampai selesai dan mengakhiri dengan paket `END_VIDEO`.
	 - Client menyimpan hasil di `client/static/temp` dan menampilkan halaman streaming.

8. Logout
	 - Klik logout untuk menghapus sesi dan kembali ke halaman login.

## Penjelasan Cara Kerja (Runtut)

- Registrasi:
	- Form di `app.py` menerima `username`, `email`, `password` dan memanggil `database.register()`.
	- Jika pendaftaran berhasil, token verifikasi dibuat oleh `create_verify_token(email)` dan disimpan di kolom `verify_token` bersama `token_expired`.
	- Fungsi `send_verify_email()` mengirim email berisi link verifikasi yang mengarah ke `BASE_URL/verify/<token>`.

- Verifikasi email:
	- Ketika pengguna membuka link verifikasi, rute `/verify/<token>` memanggil `verify_token(token)`.
	- `verify_token` memeriksa apakah token ada dan belum kedaluwarsa (field `token_expired`). Jika valid, kolom `verified` di-set ke `1` dan token dihapus.

- OTP Login:
	- Saat login berhasil (email & password cocok dan `verified=1`), server membuat OTP 6 digit melalui `create_otp(email)` dan menyimpan `otp` dan `otp_expired` di database.
	- Fungsi `send_otp_email()` mengirim kode OTP ke alamat email pengguna.
	- Pengguna memasukkan OTP pada halaman `/otp`. Fungsi `verify_otp(email, otp)` memvalidasi kode dan waktu kedaluwarsa; jika valid, user dianggap terautentikasi dan disimpan di session.

- Upload TCP:
	- Client membuka koneksi TCP ke `SERVER_IP:9000`.
	- Mengirim panjang nama file sebagai 4 byte big-endian (`!I`), lalu nama file (bytes), lalu ukuran file sebagai 8 byte unsigned big-endian (`!Q`), kemudian isi file dalam blok.
	- Server TCP membaca semua bagian sesuai format, menulis file ke `server/tcp/received_files` dan mengirim balasan `SUCCESS` atau `FAILED`.

- Streaming UDP:
	- Client mengirim nama file via UDP ke `SERVER_IP:9001`.
	- Server memeriksa keberadaan file pada `server/tcp/received_files`. Jika tidak ada, mengirim `NOT_FOUND`.
	- Jika ada, server mengirim ukuran file, menunggu ACK `READY` dari client, lalu mengirim potongan-potongan data (chunk) hingga selesai, diakhiri dengan `END_VIDEO`.
	- Client menerima paket UDP, menulis ke file sementara, lalu menampilkan file pada halaman streaming.

## Protokol Jaringan: Mengapa TCP untuk upload dan UDP untuk streaming

- TCP (Transmission Control Protocol):
	- Kelebihan: andal (retransmisi paket hilang), urutan data terjaga, cocok untuk transfer file yang harus lengkap dan konsisten.
	- Kekurangan: overhead lebih besar dan latency lebih tinggi dibanding UDP.
	- Alasan penggunaan: upload file memerlukan integritas penuh—file harus diterima lengkap tanpa kehilangan. Oleh karena itu TCP dipilih untuk proses upload.

- UDP (User Datagram Protocol):
	- Kelebihan: latensi rendah, lebih cepat untuk pengiriman data berkelanjutan seperti streaming; overhead kecil.
	- Kekurangan: tidak ada jaminan pengiriman atau urutan; paket bisa hilang atau datang berantakan.
	- Alasan penggunaan: untuk streaming video real-time, toleransi terhadap beberapa kehilangan paket lebih dapat diterima dibanding menunggu retransmisi; sehingga UDP cocok untuk mengurangi jeda.

## Struktur Database

Tabel `users` (didefinisikan di `client/database/database.py`):

- `id` (INTEGER PRIMARY KEY AUTOINCREMENT): Identitas unik pengguna.
- `name` (TEXT): Nama pengguna.
- `email` (TEXT UNIQUE): Alamat email, digunakan untuk login dan pengiriman email.
- `password` (TEXT): Kata sandi pengguna (disimpan langsung sesuai kode; tidak ada hashing pada implementasi saat ini).
- `verified` (INTEGER DEFAULT 0): Flag apakah email sudah diverifikasi (1) atau belum (0).
- `verify_token` (TEXT): Token verifikasi yang dikirim lewat email.
- `token_expired` (TEXT): Timestamp kadaluarsa token verifikasi (format `%Y-%m-%d %H:%M:%S`).
- `otp` (TEXT): Kode OTP yang dikirim untuk login.
- `otp_expired` (TEXT): Timestamp kadaluarsa OTP.

Catatan keamanan: saat ini password disimpan dalam bentuk plain text sesuai kode yang ada. Untuk penggunaan nyata disarankan menerapkan hash (mis. `bcrypt`) dan praktik keamanan lainnya.

## Author

- Nama: Muhammad Izzuddin Almansyur
- Kontak: muhizzuddin410@gmail.com
- Mata kuliah: Pemrograman Jaringan
