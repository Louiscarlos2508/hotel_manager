# /home/soutonnoma/PycharmProjects/HotelManager/models/service_disponible_model.py
from datetime import datetime, timezone

from models.base_model import BaseModel
import sqlite3

class ServiceDisponibleModel(BaseModel):

    @classmethod
    def create(cls, nom_service, description=None, prix=0.0):
        """Crée un nouveau service disponible."""
        query = "INSERT INTO services_disponibles (nom_service, description, prix) VALUES (?, ?, ?)"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nom_service, description, prix))
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"Le service '{nom_service}' existe déjà.") from e
        except sqlite3.Error as e:
            raise Exception(f"Erreur création service disponible : {e}") from e

    @classmethod
    def get_all(cls):
        """Récupère tous les services disponibles."""
        query = "SELECT * FROM services_disponibles WHERE is_deleted = 0 ORDER BY nom_service"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération services : {e}") from e

    @classmethod
    def get_by_id(cls, service_id):
        """Récupère un service par son ID."""
        query = "SELECT * FROM services_disponibles WHERE id = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (service_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération service : {e}") from e

    @classmethod
    def update(cls, service_id, **kwargs):
        """Met à jour un service (version simplifiée et robuste)."""
        allowed_fields = {"nom_service", "description", "prix"}
        fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not fields_to_update:
            return True  # Aucune mise à jour nécessaire

        # On ajoute le timestamp pour la synchronisation
        fields_to_update['updated_at'] = datetime.now(timezone.utc).isoformat()

        set_clause = ", ".join([f"{key} = ?" for key in fields_to_update])
        query = f"UPDATE services_disponibles SET {set_clause} WHERE id = ? AND is_deleted = 0"

        params = list(fields_to_update.values()) + [service_id]

        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, tuple(params))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour service : {e}") from e


    @classmethod
    def delete(cls, service_id):
        """Supprime un service."""

        query = "UPDATE services_disponibles SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, service_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression service : {e}") from e