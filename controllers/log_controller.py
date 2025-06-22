import sqlite3
from datetime import datetime

class LogController:
    def __init__(self, db_connection):
        self.db = db_connection

    def log_action(self, user_id, action):
        """
        Enregistre une action dans la table logs.
        user_id peut être None (ex: action système).
        """
        if not action or action.strip() == "":
            raise ValueError("L'action ne peut pas être vide.")
        try:
            cursor = self.db.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO logs (user_id, action, date_heure) VALUES (?, ?, ?)",
                (user_id, action.strip(), now)
            )
            self.db.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.db.rollback()
            raise Exception(f"Erreur lors de l'insertion du log: {e}")

    def get_logs(self, limit=100, user_id=None):
        """
        Récupère les logs, optionnellement filtrés par user_id.
        Limite le nombre de résultats (par défaut 100).
        """
        if limit <= 0:
            raise ValueError("La limite doit être un entier positif.")
        try:
            cursor = self.db.cursor()
            if user_id is not None:
                cursor.execute(
                    "SELECT id, user_id, action, date_heure FROM logs WHERE user_id = ? ORDER BY date_heure DESC LIMIT ?",
                    (user_id, limit)
                )
            else:
                cursor.execute(
                    "SELECT id, user_id, action, date_heure FROM logs ORDER BY date_heure DESC LIMIT ?",
                    (limit,)
                )
            rows = cursor.fetchall()
            logs = []
            for row in rows:
                logs.append({
                    "id": row[0],
                    "user_id": row[1],
                    "action": row[2],
                    "date_heure": row[3],
                })
            return logs
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération des logs: {e}")
