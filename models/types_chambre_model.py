# /home/soutonnoma/PycharmProjects/HotelManger/models/types_chambre_model.py
from datetime import timezone, datetime

from models.base_model import BaseModel
import sqlite3

class TypesChambreModel(BaseModel):

    @classmethod
    def create(cls, nom, description, prix_par_nuit):
        """Crée un nouveau type de chambre."""
        query = "INSERT INTO types_chambre (nom, description, prix_par_nuit) VALUES (?, ?, ?)"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nom, description, prix_par_nuit))
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"Le type de chambre '{nom}' existe déjà.") from e
        except sqlite3.Error as e:
            raise Exception(f"Erreur création type chambre : {e}") from e

    @classmethod
    def get_all(cls):
        """Récupère tous les types de chambre."""
        query = "SELECT * FROM types_chambre WHERE is_deleted = 0 ORDER BY nom ASC"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération types de chambre : {e}") from e

    @classmethod
    def get_by_id(cls, type_id):
        """Récupère un type de chambre par son ID."""
        query = "SELECT * FROM types_chambre WHERE id = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (type_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération type chambre : {e}") from e

    @classmethod
    def update(cls, type_id, nom, description, prix_par_nuit):
        """Met à jour un type de chambre."""
        query = "UPDATE types_chambre SET nom = ?, description = ?, prix_par_nuit = ?, updated_at = ? WHERE id = ? AND is_deleted = 0"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nom, description, prix_par_nuit, timestamp_actuel, type_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour type chambre : {e}") from e

    @classmethod
    def delete(cls, type_id):
        """Supprime un type de chambre."""

        query = "UPDATE types_chambre SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, type_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression type chambre : {e}") from e