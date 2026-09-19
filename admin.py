import os
import getpass
import psycopg

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

username = input("Username: ")
password = getpass.getpass("Password: ")

password_hash = generate_password_hash(password)

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (
                username,
                password_hash
            )
            VALUES (%s, %s);
        """, (
            username,
            password_hash
        ))

    conn.commit()

print("Admin account created.")