# /home/soutonnoma/PycharmProjects/HotelManger/models/chambre_model.py
from models.base_model import BaseModel
import sqlite3

class ChambreModel(BaseModel):

    @classmethod
    def create(cls, numero, type_id, statut='libre'):
        """Crée une nouvelle chambre."""
        query = "INSERT INTO chambres (numero, type_id, statut) VALUES (?, ?, ?)"
        try:
            with cls.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (numero, type_id, statut))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"Le numéro de chambre '{numero}' existe déjà.") from e
        except sqlite3.Error as e:
            raise Exception(f"Erreur base de données lors de la création de la chambre : {e}") from e

    @classmethod
    def get_all(cls):
        """Récupère toutes les chambres avec les détails de leur type."""
        query = """
            SELECT c.id, c.numero, c.statut, tc.nom AS type_nom, tc.prix_par_nuit
            FROM chambres c
            JOIN types_chambre tc ON c.type_id = tc.id
            ORDER BY c.numero
        """
        try:
            with cls.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur de récupération des chambres : {e}") from e

    @classmethod
    def get_by_id(cls, chambre_id):
        """Récupère une chambre spécifique par son ID."""
        query = """
            SELECT c.id, c.numero, c.type_id, c.statut, tc.nom AS type_nom, tc.prix_par_nuit
            FROM chambres c
            JOIN types_chambre tc ON c.type_id = tc.id
            WHERE c.id = ?
        """
        try:
            with cls.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (chambre_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur de récupération de la chambre {chambre_id} : {e}") from e

    @classmethod
    def update(cls, chambre_id, numero, type_id, statut):
        """Met à jour les informations d'une chambre."""
        query = "UPDATE chambres SET numero = ?, type_id = ?, statut = ? WHERE id = ?"
        try:
            with cls.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (numero, type_id, statut, chambre_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur de mise à jour de la chambre {chambre_id} : {e}") from e

    @classmethod
    def delete(cls, chambre_id):
        """Supprime une chambre."""
        query = "DELETE FROM chambres WHERE id = ?"
        try:
            with cls.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (chambre_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur de suppression de la chambre {chambre_id} : {e}") from e

    @classmethod
    def get_all_types(cls):
        """Récupère tous les types de chambre disponibles."""
        query = "SELECT id, nom, prix_par_nuit FROM types_chambre ORDER BY nom"
        try:
            with cls.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur de récupération des types de chambre : {e}") from e

    @classmethod
    def get_chambres_disponibles(cls, date_arrivee, date_depart):
        """
        Retourne les chambres qui n'ont aucune réservation active chevauchante avec les dates données.
        """
        query = """
            SELECT c.id, c.numero, tc.nom AS type_nom, tc.prix_par_nuit
            FROM chambres c
            JOIN types_chambre tc ON c.type_id = tc.id
            WHERE c.statut = 'libre' AND c.id NOT IN (
                SELECT r.chambre_id FROM reservations r
                WHERE r.statut != 'annulée' AND (
                    r.date_arrivee < ? AND r.date_depart > ?
                )
            )
            ORDER BY c.numero
        """
        try:
            with cls.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (date_depart, date_arrivee))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur de recherche des chambres disponibles : {e}") from e