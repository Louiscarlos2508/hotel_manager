# /home/soutonnoma/PycharmProjects/HotelManger/models/facture_model.py
from datetime import datetime, timezone

from models.base_model import BaseModel
import sqlite3

class FactureModel(BaseModel):

    @classmethod
    def create(cls, reservation_id, statut="Brouillon"):
        query = "INSERT INTO factures (reservation_id, statut) VALUES (?, ?)"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (reservation_id, statut))
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"Une facture existe déjà pour la réservation {reservation_id}.") from e
        except sqlite3.Error as e:
            raise Exception(f"Erreur création facture : {e}") from e

    @classmethod
    def get_by_reservation(cls, reservation_id):
        query = "SELECT * FROM factures WHERE reservation_id = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (reservation_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération facture : {e}") from e

    @classmethod
    def update_statut(cls, facture_id, nouveau_statut):
        query = "UPDATE factures SET statut = ?, updated_at = ? WHERE id = ? AND is_deleted = 0"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nouveau_statut, timestamp_actuel, facture_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour statut facture : {e}") from e

    @classmethod
    def update_montants(cls, facture_id, montant_total_ht, montant_total_tva, montant_total_ttc, montant_paye):
        """Met à jour les montants détaillés (HT, TVA, TTC) et le montant payé d'une facture."""
        query = """
            UPDATE factures 
            SET montant_total_ht = ?, montant_total_tva = ?, montant_total_ttc = ?, montant_paye = ?, updated_at = ? 
            WHERE id = ? AND is_deleted = 0
        """
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (montant_total_ht, montant_total_tva, montant_total_ttc, montant_paye, timestamp_actuel, facture_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour montants facture : {e}") from e

    @classmethod
    def delete(cls, facture_id):

        query = "UPDATE factures SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, facture_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression facture : {e}") from e

    @classmethod
    def get_by_id(cls, facture_id):
        """Récupère une facture par son ID."""
        query = "SELECT * FROM factures WHERE id = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (facture_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération facture par ID : {e}") from e
