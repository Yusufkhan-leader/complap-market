import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()  # .env faylidagi sozlamalarni o'qiydi


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "laptop_market"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        cursor_factory=RealDictCursor,
    )
