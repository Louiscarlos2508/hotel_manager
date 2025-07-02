# /home/soutonnoma/PycharmProjects/HotelManager/models/probleme_model.py
from models.base_model import BaseModel
import sqlite3
from datetime import datetime, timezone


class ProblemeModel(BaseModel):

    @classmethod
    def create(cls, chambre_id, description, signale_par_user_id=None, priorite='Moyenne'):
        """Signale un nouveau problème."""
        query = "INSERT INTO problemes (chambre_id, description, signale_par_user_id, priorite) VALUES (?, ?, ?, ?)"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (chambre_id, description, signale_par_user_id, priorite))
                conn.commit()
                return cur.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Erreur création problème : {e}") from e

    @classmethod
    def get_all(cls):
        """Récupère tous les problèmes avec les détails de la chambre et de l'utilisateur."""
        query = """
            SELECT p.*, ch.numero AS numero_chambre, u.nom_complet AS signale_par
            FROM problemes p
            JOIN chambres ch ON p.chambre_id = ch.id
            LEFT JOIN users u ON p.signale_par_user_id = u.id
            WHERE p.is_deleted = 0
            ORDER BY p.date_signalement DESC
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération problèmes : {e}") from e

    @classmethod
    def get_by_id(cls, probleme_id):
        """Récupère un problème par son ID."""
        query = "SELECT * FROM problemes WHERE id = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (probleme_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération problème : {e}") from e

    @classmethod
    def update_statut(cls, probleme_id, nouveau_statut):
        """Met à jour le statut d'un problème et la date de résolution si nécessaire."""
        query = "UPDATE problemes SET statut = ?, date_resolution = ?, updated_at = ? WHERE id = ? AND is_deleted = 0"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        date_resolution = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if nouveau_statut == "Résolu" else None

        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nouveau_statut, date_resolution, timestamp_actuel, probleme_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour du problème : {e}") from e

    @classmethod
    def delete(cls, probleme_id):
        """Supprime un problème."""

        query = "UPDATE problemes SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, probleme_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression problème : {e}") from e