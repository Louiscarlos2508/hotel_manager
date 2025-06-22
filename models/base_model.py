import sqlite3

class BaseModel:
    DB_PATH = "hotel.db"

    @classmethod
    def connect(cls):
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row  # ✅ rend les résultats accessibles via dict(row)
        return conn
