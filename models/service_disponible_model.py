# /home/soutonnoma/PycharmProjects/HotelManger/models/service_disponible_model.py
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
        query = "SELECT * FROM services_disponibles ORDER BY nom_service"
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
        query = "SELECT * FROM services_disponibles WHERE id = ?"
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
        """Met à jour un service."""
        allowed_fields = {"nom_service", "description", "prix"}
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                fields.append(f"{key} = ?")
                values.append(value)
        if not fields:
            return False
        values.append(service_id)
        query = f"UPDATE services_disponibles SET {', '.join(fields)} WHERE id = ?"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, tuple(values))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour service : {e}") from e

    @classmethod
    def delete(cls, service_id):
        """Supprime un service."""
        query = "DELETE FROM services_disponibles WHERE id = ?"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (service_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression service : {e}") from e