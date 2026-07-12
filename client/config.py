import os
from dotenv import load_dotenv

# Ambil data dari file .env
load_dotenv()

# Konfigurasi aplikasi
SECRET_KEY = os.getenv("SECRET_KEY", "key_default_jika_env_hilang")
DATABASE = os.getenv("DATABASE", "database/users.db")

# Konfigurasi Mail Server
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))  # Port harus diconvert ke integer
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"  # Convert ke Boolean

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")