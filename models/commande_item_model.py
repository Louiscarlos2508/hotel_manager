# /home/soutonnoma/PycharmProjects/HotelManager/models/commande_item_model.py
from datetime import datetime, timezone
from typing import List, Dict, Any
import sqlite3
from models.base_model import BaseModel

class CommandeItemModel(BaseModel):

    @classmethod
    def add_item(cls, commande_id, produit_id, quantite, prix_unitaire_capture):
        """Ajoute un produit dans une commande."""
        query = """
            INSERT INTO commande_items (commande_id, produit_id, quantite, prix_unitaire_capture)
            VALUES (?, ?, ?, ?)
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (commande_id, produit_id, quantite, prix_unitaire_capture))
                conn.commit()
                return cur.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Erreur ajout produit dans commande : {e}") from e

    @classmethod
    def get_items_by_commande(cls, commande_id) -> List[Dict[str, Any]]:
        """Liste tous les items d'une commande avec le nom du produit."""
        query = """
            SELECT ci.*, p.nom AS produit_nom
            FROM commande_items ci
            JOIN produits p ON ci.produit_id = p.id
            WHERE ci.commande_id = ? AND ci.is_deleted = 0
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (commande_id,))
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération items commande : {e}") from e

    @classmethod
    def delete(cls, item_id: int) -> bool:
        """Supprime un article d'une commande."""
        query = "UPDATE commande_items SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, item_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur suppression article commande : {e}") from e

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        """Récupère tous les articles de toutes les commandes, avec le nom du produit."""
        query = """
            SELECT ci.*, p.nom AS produit_nom
            FROM commande_items ci
            LEFT JOIN produits p ON ci.produit_id = p.id
            WHERE ci.is_deleted = 0
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération de tous les articles de commande : {e}") from e

    @classmethod
    def get_all_with_details(cls) -> List[Dict[str, Any]]:
        """Récupère tous les articles de toutes les commandes, avec la date de la commande parente."""
        query = """
            SELECT
                ci.commande_id,
                ci.quantite,
                ci.prix_unitaire_capture,
                c.date_commande
            FROM commande_items ci
            JOIN commandes c ON ci.commande_id = c.id
            WHERE c.is_deleted = 0
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération des détails des articles de commande : {e}") from e

    @classmethod
    def get_all_items_details_by_lieu(cls, lieu_consommation: str) -> List[Dict[str, Any]]:
        """Récupère tous les articles pour un lieu de consommation spécifique avec tous les détails."""
        query = """
            SELECT
                ci.id AS item_id,
                ci.quantite,
                ci.prix_unitaire_capture,
                p.nom AS produit_nom,
                cl.nom || ' ' || cl.prenom AS client_nom,
                ch.numero AS chambre_numero,
                cmd.id AS commande_id,
                cmd.statut AS commande_statut
            FROM commande_items ci
            JOIN produits p ON ci.produit_id = p.id
            JOIN commandes cmd ON ci.commande_id = cmd.id
            JOIN reservations r ON cmd.reservation_id = r.id
            JOIN clients cl ON r.client_id = cl.id
            JOIN chambres ch ON r.chambre_id = ch.id
            WHERE cmd.lieu_consommation = ? AND cmd.is_deleted = 0
            ORDER BY cmd.date_commande DESC, cl.nom;
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (lieu_consommation,))
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération détails des articles pour {lieu_consommation}: {e}") from e