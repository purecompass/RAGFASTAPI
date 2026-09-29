import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv


load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER", os.getenv("USER")),
    "password": os.getenv("DB_PASSWORD", os.getenv("PASSWORD")),
    "host": os.getenv("DB_HOST", os.getenv("HOST", "localhost")),
    "port": int(os.getenv("DB_PORT", os.getenv("PORT", 3306))),
    "database": os.getenv("DB_NAME", os.getenv("DBNAME", "champ_1f2_customer_support_db")),
    "autocommit": True,
}


@contextmanager
def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as exc:
        raise RuntimeError(
            f"MySQL connection failed for host {DB_CONFIG['host']}:{DB_CONFIG['port']} "
            f"database {DB_CONFIG['database']}. Check your .env values for DB_HOST, DB_PORT, "
            "DB_NAME, DB_USER, and DB_PASSWORD."
        ) from exc
    try:
        yield conn
    finally:
        conn.close()
