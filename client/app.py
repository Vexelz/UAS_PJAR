from flask import Flask, render_template, request, redirect, session
import config

from database.database import (
    init_db,
    login,
    register,
    create_verify_token,
    verify_token,
    create_otp,
    verify_otp
)

from auth.send_email import (
    send_verify_email,
    send_otp_email
)

from tcp.tcp_client import upload_file
from udp.udp_client import request_video_stream

app = Flask(__name__)

app.secret_key = config.SECRET_KEY

init_db()


# ===================================================
# LOGIN
# ===================================================

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = login(email, password)

        if user:

            otp = create_otp(email)

            send_otp_email(
                email,
                user[1],
                otp
            )

            session["otp_email"] = email

            return redirect("/otp")

        return render_template(
            "login.html",
            error="Email atau Password salah atau akun belum diverifikasi."
        )

    return render_template("login.html")


# ===================================================
# OTP
# ===================================================

@app.route("/otp", methods=["GET", "POST"])
def otp():

    if "otp_email" not in session:
        return redirect("/")

    if request.method == "POST":

        kode = request.form["otp"]

        user = verify_otp(
            session["otp_email"],
            kode
        )

        if user:

            session["user"] = user[1]

            session.pop("otp_email")

            return redirect("/dashboard")

        return render_template(
            "otp.html",
            error="OTP salah atau sudah kedaluwarsa."
        )

    return render_template("otp.html")


# ===================================================
# VERIFIKASI AKUN
# ===================================================

@app.route("/verify/<token>")
def verify(token):

    user = verify_token(token)

    if user is None:

        return render_template("verify_failed.html")

    return render_template("verify_success.html")


# ===================================================
# REGISTER
# ===================================================

@app.route("/register", methods=["GET", "POST"])
def register_page():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        success = register(
            username,
            email,
            password
        )

        if not success:

            return render_template(
                "register.html",
                error="Email sudah digunakan."
            )

        token = create_verify_token(email)

        send_verify_email(
            email,
            username,
            token
        )

        return render_template(
            "check_email.html",
            email=email
        )

    return render_template("register.html")


# ===================================================
# DASHBOARD
# ===================================================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


# ===================================================
# UPLOAD TCP
# ===================================================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        if "file" not in request.files:
            return "Tidak ada file."

        file = request.files["file"]

        if file.filename == "":
            return "Pilih file terlebih dahulu."

        result = upload_file(file)

        if result == "SUCCESS":

            session["last_video"] = file.filename

            return render_template(
                "upload.html",
                success="File berhasil dikirim ke TCP Server."
            )

        return render_template(
            "upload.html",
            error="Upload gagal."
        )

    return render_template("upload.html")


# ===================================================
# STREAMING UDP
# ===================================================

@app.route("/streaming_page")
def streaming_page():

    if "user" not in session:
        return redirect("/")

    filename = session.get("last_video")

    if filename is None:
        return "Belum ada video yang diupload."

    request_video_stream(filename)

    return render_template(
        "streaming.html",
        filename=filename
    )


# ===================================================
# LOGOUT
# ===================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ===================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )