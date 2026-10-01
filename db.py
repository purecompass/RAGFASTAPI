import os
import logging
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER", os.getenv("USER")),
    "password": os.getenv("DB_PASSWORD", os.getenv("PASSWORD")),
    "host": os.getenv("DB_HOST", os.getenv("HOST", "localhost")),
    "port": int(os.getenv("DB_PORT", "3306")),
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
            f"database {DB_CONFIG['database']} (MySQL error {exc.errno}: {exc.msg}). "
            "Check DB_HOST, DB_PORT, DB_NAME, DB_USER, and DB_PASSWORD."
        ) from exc
    try:
        yield conn
    finally:
        conn.close()


def record_exception(source: str, exc: Exception) -> None:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO Application_Exception_Log
                    (AEL_Source, AEL_Exception_Type, AEL_Message)
                    VALUES (%s, %s, %s)""",
                    (source[:255], type(exc).__name__[:255], str(exc)[:16000]),
                )
            finally:
                cursor.close()
    except Exception as logging_exc:
        logger.error(
            "Could not persist exception to Application_Exception_Log "
            "(source=%s; logging failure=%s: %s). Original exception=%s: %s",
            source,
            type(logging_exc).__name__,
            logging_exc,
            type(exc).__name__,
            exc,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
