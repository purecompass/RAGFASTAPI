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
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()
