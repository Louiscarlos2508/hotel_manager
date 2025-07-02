# /home/soutonnoma/PycharmProjects/HotelManager/models/service_demande_model.py
from datetime import datetime, timezone

from models.base_model import BaseModel
import sqlite3

class ServiceDemandeModel(BaseModel):

    @classmethod
    def create(cls, reservation_id, service_id, quantite, prix_capture, statut="Demandé"):
        """Crée une nouvelle demande de service."""
        query = "INSERT INTO services_demandes (reservation_id, service_id, quantite, prix_capture, statut) VALUES (?, ?, ?, ?, ?)"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (reservation_id, service_id, quantite, prix_capture, statut))
                conn.commit()
                return cur.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Erreur création demande de service : {e}") from e

    @classmethod
    def get_all(cls):
        """Récupère toutes les demandes de service avec les détails."""
        query = """
            SELECT sd.*, s.nom_service, r.chambre_id, c.nom || ' ' || c.prenom as client_nom
            FROM services_demandes sd
            JOIN services_disponibles s ON sd.service_id = s.id
            JOIN reservations r ON sd.reservation_id = r.id
            JOIN clients c ON r.client_id = c.id
            WHERE sd.is_deleted = 0
            ORDER BY sd.date_demande DESC
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération services demandés : {e}") from e

    @classmethod
    def get_by_reservation(cls, reservation_id):
        """Récupère les demandes de service pour une réservation."""
        query = """
            SELECT sd.*, s.nom_service
            FROM services_demandes sd
            JOIN services_disponibles s ON sd.service_id = s.id
            WHERE sd.reservation_id = ? AND sd.is_deleted = 0
            ORDER BY sd.date_demande
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (reservation_id,))
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération des services de la réservation : {e}") from e

    @classmethod
    def update_statut(cls, demande_id, nouveau_statut):
        """Met à jour le statut d'une demande de service."""
        query = "UPDATE services_demandes SET statut = ?, updated_at = ? WHERE id = ? AND is_deleted = 0"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nouveau_statut, timestamp_actuel, demande_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour statut service demandé : {e}") from e

    @classmethod
    def delete(cls, demande_id):
        """Supprime une demande de service."""

        query = "UPDATE services_demandes SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, demande_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression service demandé : {e}") from e