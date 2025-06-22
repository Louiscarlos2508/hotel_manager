from models.base_model import BaseModel

class LogModel(BaseModel):

    @classmethod
    def add(cls, user_id, action):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO logs (user_id, action)
            VALUES (?, ?)
        """, (user_id, action))
        conn.commit()
        conn.close()

    @classmethod
    def get_all(cls):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT l.id, u.username, l.action, l.date_heure
            FROM logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.date_heure DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
