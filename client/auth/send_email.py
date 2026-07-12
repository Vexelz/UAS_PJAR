import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


# ======================================================
# EMAIL VERIFIKASI AKUN (SETELAH REGISTER)
# ======================================================

def send_verify_email(receiver_email, username, token):

    verify_link = f"{config.BASE_URL}/verify/{token}"

    subject = "Verifikasi Akun"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">

        <h2>Verifikasi Akun</h2>

        <p>Halo <b>{username}</b>,</p>

        <p>
            Terima kasih telah mendaftar pada aplikasi PJAR.
        </p>

        <p>
            Klik tombol berikut untuk mengaktifkan akun Anda.
        </p>

        <a href="{verify_link}"
           style="
           background-color:#198754;
           color:white;
           padding:12px 24px;
           text-decoration:none;
           border-radius:5px;
           display:inline-block;">

            Verifikasi Akun

        </a>

        <br><br>

        <p>
            Jika tombol tidak dapat digunakan, buka link berikut:
        </p>

        <p>{verify_link}</p>

        <hr>

        <small>
            Link hanya berlaku selama 5 menit.
            <br>
            Setelah akun aktif, silakan login kembali.
        </small>

    </body>
    </html>
    """

    message = MIMEMultipart("alternative")

    message["Subject"] = subject
    message["From"] = config.MAIL_USERNAME
    message["To"] = receiver_email

    message.attach(
        MIMEText(html, "html")
    )

    try:

        server = smtplib.SMTP(
            config.MAIL_SERVER,
            config.MAIL_PORT
        )

        server.starttls()

        server.login(
            config.MAIL_USERNAME,
            config.MAIL_PASSWORD
        )

        server.sendmail(
            config.MAIL_USERNAME,
            receiver_email,
            message.as_string()
        )

        server.quit()

        print("Email verifikasi berhasil dikirim.")

    except Exception as e:

        print("Gagal mengirim email:", e)


# ======================================================
# EMAIL OTP LOGIN
# ======================================================

def send_otp_email(receiver_email, username, otp):

    subject = "Kode OTP Login"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">

        <h2>Verifikasi Login</h2>

        <p>Halo <b>{username}</b>,</p>

        <p>
            Masukkan kode OTP berikut untuk melanjutkan login.
        </p>

        <h1 style="
            color:#0d6efd;
            letter-spacing:8px;
            font-size:40px;
        ">
            {otp}
        </h1>

        <p>
            Kode OTP berlaku selama <b>5 menit</b>.
        </p>

        <hr>

        <small>
            Jangan memberikan kode OTP ini kepada siapa pun.
        </small>

    </body>
    </html>
    """

    message = MIMEMultipart("alternative")

    message["Subject"] = subject
    message["From"] = config.MAIL_USERNAME
    message["To"] = receiver_email

    message.attach(
        MIMEText(html, "html")
    )

    try:

        server = smtplib.SMTP(
            config.MAIL_SERVER,
            config.MAIL_PORT
        )

        server.starttls()

        server.login(
            config.MAIL_USERNAME,
            config.MAIL_PASSWORD
        )

        server.sendmail(
            config.MAIL_USERNAME,
            receiver_email,
            message.as_string()
        )

        server.quit()

        print("OTP berhasil dikirim.")

    except Exception as e:

        print("Gagal mengirim OTP:", e)