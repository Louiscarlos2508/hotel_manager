# /home/soutonnoma/PycharmProjects/HotelManager/models/log_model.py
import sqlite3
from models.base_model import BaseModel

class LogModel(BaseModel):
    """Modèle pour gérer les logs d'audit dans la base de données."""

    @classmethod
    def create(cls, user_id, action, details=None):
        """
        Enregistre une nouvelle action dans les logs en utilisant une connexion sécurisée.
        """
        query = "INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)"
        try:
            # Utilisation du nouveau pattern de connexion robuste
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (user_id, action, details))
                conn.commit()
        except sqlite3.Error as e:
            # Un échec de log ne doit JAMAIS faire planter l'application.
            # On affiche une erreur critique dans la console pour le débogage.
            print(f"CRITICAL LOGGING ERROR: Could not write to log table. Error: {e}")

    @classmethod
    def get_all(cls, limit=100):
        """
        Récupère les logs les plus récents, avec le nom de l'utilisateur.
        """
        query = """
            SELECT l.id, u.username, l.action, l.details, l.date_heure
            FROM logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.date_heure DESC
            LIMIT ?
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (limit,))
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            print(f"CRITICAL LOGGING ERROR: Could not retrieve logs. Error: {e}")
            return []  # Retourne une liste vide en cas d'erreur pour ne pas planter l'UI