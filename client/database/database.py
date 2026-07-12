import sqlite3
import os
import secrets
import random
from datetime import datetime, timedelta

DB_PATH = "database/users.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


def init_db():

    os.makedirs("database", exist_ok=True)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT UNIQUE,

        password TEXT,

        verified INTEGER DEFAULT 0,

        verify_token TEXT,

        token_expired TEXT,

        otp TEXT,

        otp_expired TEXT

    )

    """)

    conn.commit()
    conn.close()


def register(username, email, password):

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""

        INSERT INTO users(

            name,
            email,
            password,
            verified,
            verify_token,
            token_expired,
            otp,
            otp_expired

        )

        VALUES(?,?,?,?,?,?,?,?)

        """, (

            username,
            email,
            password,
            0,
            None,
            None,
            None,
            None

        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def login(email, password):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM users

        WHERE email=?

        AND password=?

        AND verified=1

    """, (email, password))

    user = cursor.fetchone()

    conn.close()

    return user


def create_verify_token(email):

    token = secrets.token_urlsafe(32)

    expired = datetime.now() + timedelta(minutes=5)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE users

        SET

        verify_token=?,
        token_expired=?

        WHERE email=?

    """, (

        token,
        expired.strftime("%Y-%m-%d %H:%M:%S"),
        email

    ))

    conn.commit()
    conn.close()

    return token


def verify_token(token):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM users

        WHERE verify_token=?

    """, (token,))

    user = cursor.fetchone()

    if user is None:

        conn.close()
        return None

    expired = datetime.strptime(
        user[6],
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() > expired:

        conn.close()
        return None

    cursor.execute("""

        UPDATE users

        SET

        verified=1,
        verify_token=NULL,
        token_expired=NULL

        WHERE id=?

    """, (user[0],))

    conn.commit()
    conn.close()

    return user


def create_otp(email):

    otp = str(random.randint(100000, 999999))

    expired = datetime.now() + timedelta(minutes=5)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE users

        SET

        otp=?,
        otp_expired=?

        WHERE email=?

    """, (

        otp,
        expired.strftime("%Y-%m-%d %H:%M:%S"),
        email

    ))

    conn.commit()
    conn.close()

    return otp


def verify_otp(email, otp):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM users

        WHERE email=?

        AND otp=?

    """, (

        email,
        otp

    ))

    user = cursor.fetchone()

    if user is None:

        conn.close()
        return None

    expired = datetime.strptime(
        user[8],
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() > expired:

        conn.close()
        return None

    cursor.execute("""

        UPDATE users

        SET

        otp=NULL,
        otp_expired=NULL

        WHERE id=?

    """, (user[0],))

    conn.commit()
    conn.close()

    return user


def get_user_by_email(email):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM users

        WHERE email=?

    """, (email,))

    user = cursor.fetchone()

    conn.close()

    return user