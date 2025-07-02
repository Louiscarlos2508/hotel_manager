# /home/soutonnoma/PycharmProjects/HotelManger/models/paiement_model.py
from models.base_model import BaseModel
from datetime import datetime, timezone
import sqlite3

class PaiementModel(BaseModel):

    @classmethod
    def create(cls, facture_id, montant, methode, date_paiement=None):
        """Crée un nouvel enregistrement de paiement."""
        query = "INSERT INTO paiements (facture_id, montant, methode, date_paiement) VALUES (?, ?, ?, ?)"
        try:
            with cls.connect() as conn:
                if date_paiement is None:
                    date_paiement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(date_paiement, datetime):
                    date_paiement = date_paiement.strftime("%Y-%m-%d %H:%M:%S")

                cur = conn.cursor()
                cur.execute(query, (facture_id, montant, methode, date_paiement))
                conn.commit()
                return cur.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Erreur création paiement : {e}") from e

    @classmethod
    def get_by_facture(cls, facture_id):
        """Récupère tous les paiements pour une facture donnée."""
        query = "SELECT * FROM paiements WHERE facture_id = ? AND is_deleted = 0 ORDER BY date_paiement DESC"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (facture_id,))
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération paiements : {e}") from e

    @classmethod
    def delete(cls, paiement_id):
        """Supprime un paiement."""

        query = "UPDATE paiements SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, paiement_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression paiement : {e}") from e

    @classmethod
    def get_all(cls):
        """Récupère tous les paiements de la base de données."""
        query = "SELECT * FROM paiements WHERE is_deleted = 0 ORDER BY date_paiement DESC"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération de tous les paiements : {e}") from e