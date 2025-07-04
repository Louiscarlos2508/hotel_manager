# /home/soutonnoma/PycharmProjects/HotelManager/models/produit_model.py
from datetime import datetime, timezone

from models.base_model import BaseModel
import sqlite3

class ProduitModel(BaseModel):

    @classmethod
    def create(cls, nom, description, categorie, prix_unitaire, disponible=True):
        """Crée un nouveau produit."""
        query = "INSERT INTO produits (nom, description, categorie, prix_unitaire, disponible) VALUES (?, ?, ?, ?, ?)"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nom, description, categorie, prix_unitaire, int(disponible)))
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"Le produit '{nom}' existe déjà.") from e
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la création du produit : {e}") from e

    @classmethod
    def get_all(cls):
        """Récupère tous les produits."""
        query = "SELECT * FROM produits WHERE is_deleted = 0 ORDER BY nom"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération des produits : {e}") from e

    @classmethod
    def get_by_id(cls, produit_id):
        """Récupère un produit par son ID."""
        query = "SELECT * FROM produits WHERE id = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (produit_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération produit {produit_id} : {e}") from e

    @classmethod
    def update(cls, produit_id, nom, description, categorie, prix_unitaire, disponible):
        """Met à jour un produit."""
        query = """
            UPDATE produits SET nom = ?, description = ?, categorie = ?, prix_unitaire = ?, disponible = ?, updated_at = ?
            WHERE id = ? AND is_deleted = 0
        """
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nom, description, categorie, prix_unitaire, int(disponible), timestamp_actuel, produit_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur mise à jour produit : {e}") from e

    @classmethod
    def delete(cls, produit_id):
        """Supprime un produit."""

        query = "UPDATE produits SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, produit_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression produit : {e}") from e