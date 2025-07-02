# /home/soutonnoma/PycharmProjects/HotelManger/models/commande_model.py
from datetime import datetime, timezone

from models.base_model import BaseModel
import sqlite3

class CommandeModel(BaseModel):

    @classmethod
    def create(cls, reservation_id, user_id_saisie=None, lieu_consommation='Room Service'):
        """Crée une nouvelle commande (vide pour le moment)."""
        query = """
            INSERT INTO commandes (reservation_id, user_id_saisie, lieu_consommation)
            VALUES (?, ?, ?)
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (reservation_id, user_id_saisie, lieu_consommation))
                conn.commit()
                return cur.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Erreur création commande : {e}") from e

    @classmethod
    def get_all(cls):
        """Récupère toutes les commandes avec leurs infos."""
        query = """
            SELECT c.*, r.chambre_id, u.nom_complet AS saisi_par
            FROM commandes c
            JOIN reservations r ON c.reservation_id = r.id
            LEFT JOIN users u ON c.user_id_saisie = u.id
            WHERE c.is_deleted = 0
            ORDER BY c.date_commande DESC
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération commandes : {e}") from e

    @classmethod
    def update_statut(cls, commande_id, nouveau_statut):
        """Met à jour le statut d'une commande."""
        query = "UPDATE commandes SET statut = ?, updated_at = ? WHERE id = ? AND is_deleted = 0"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nouveau_statut, timestamp_actuel, commande_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour statut commande : {e}") from e

    @classmethod
    def delete(cls, commande_id):
        """Supprime une commande (et ses items grâce à ON DELETE CASCADE)."""

        query = "UPDATE commandes SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, commande_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression commande : {e}") from e

    @classmethod
    def find_by_reservation_and_lieu(cls, reservation_id, lieu_consommation):
        """Trouve une commande existante pour une réservation et un lieu donnés."""
        query = "SELECT * FROM commandes WHERE reservation_id = ? AND lieu_consommation = ? AND is_deleted = 0 LIMIT 1"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (reservation_id, lieu_consommation))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur recherche commande : {e}") from e

    @classmethod
    def get_by_reservation(cls, reservation_id):
        """Récupère toutes les commandes pour une réservation donnée."""
        query = "SELECT * FROM commandes WHERE reservation_id = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (reservation_id,))
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération commandes par réservation : {e}") from e