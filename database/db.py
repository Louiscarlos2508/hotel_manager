import sqlite3
import os

DB_NAME = "hotel.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    if not os.path.exists(DB_NAME):
        conn = get_connection()
        with open("database/schema_hotel.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("✅ Base de données créée.")
    else:
        print("ℹ️ Base de données déjà existante.")
