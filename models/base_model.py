import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "hotel.db")

class BaseModel:
    @classmethod
    def connect(cls):
        """
        Établit et RETOURNE une nouvelle connexion à la base de données.
        Cette méthode ne stocke plus la connexion, elle la fournit à la demande.
        """
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Fichier base de données introuvable : {DB_PATH}")

        # On crée une nouvelle connexion à chaque appel
        conn = sqlite3.connect(DB_PATH)
        # On active les contraintes de clé étrangère pour la sécurité des données
        conn.execute("PRAGMA foreign_keys = ON;")
        # On configure les résultats pour qu'ils soient accessibles comme des dictionnaires
        conn.row_factory = sqlite3.Row

        return conn

    @staticmethod
    def dict_factory(cursor, row):
        """
        Fonction utilitaire alternative pour convertir row en dict (optionnel).
        Pas nécessaire si tu utilises sqlite3.Row et dict(row).
        """
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
