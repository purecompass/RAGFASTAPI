import os
from dotenv import load_dotenv
import psycopg2
from contextlib import contextmanager


load_dotenv()

# DB_CONFIG = {
#     "dbname": "postgres",
#     "user": "postgres",
#     "password": "yourpassword",
#     "host": "localhost",
#     "port": 5432
# }

DB_CONFIG = {
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "host": os.getenv("HOST"),
    "port": int(os.getenv("PORT", 5432)),
    "dbname": os.getenv("DBNAME")
}

@contextmanager
def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()
