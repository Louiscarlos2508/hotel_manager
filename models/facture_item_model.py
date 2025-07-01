# /home/soutonnoma/PycharmProjects/HotelManger/models/facture_item_model.py
from typing import List, Dict, Any, Optional

from models.base_model import BaseModel
import sqlite3

class FactureItemModel(BaseModel):

    @classmethod
    def create(cls,
               facture_id: int,
               description: str,
               quantite: int,
               prix_unitaire_ht: float,
               montant_ht: float,
               montant_tva: float,
               montant_ttc: float,
               date_prestation: Optional[str] = None,
               commande_id: Optional[int] = None,
               service_demande_id: Optional[int] = None) -> int:
        """Ajoute une ligne à une facture avec les montants pré-calculés."""
        query = """
                INSERT INTO facture_items (
                    facture_id, description, quantite, prix_unitaire_ht, 
                    montant_ht, montant_tva, montant_ttc,
                    date_prestation, commande_id, service_demande_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_DATE), ?, ?)
            """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (
                    facture_id, description, quantite, prix_unitaire_ht,
                    montant_ht, montant_tva, montant_ttc,
                    date_prestation, commande_id, service_demande_id
                ))
                conn.commit()
                return cur.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Erreur création ligne facture : {e}") from e

    @classmethod
    def get_by_facture(cls, facture_id: int) -> List[Dict[str, Any]]:
        """Récupère toutes les lignes d'une facture."""
        query = "SELECT * FROM facture_items WHERE facture_id = ?"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (facture_id,))
                rows = cur.fetchall()
                # --- CORRECTION ---
                # On itère sur la variable 'rows' qui contient les résultats.
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération items facture : {e}") from e


    @classmethod
    def delete_by_facture(cls, facture_id: int):
        """Supprime TOUS les articles d'une facture donnée pour la nettoyer avant recalcul."""
        query = "DELETE FROM facture_items WHERE facture_id = ?"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (facture_id,))
                conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors du nettoyage de la facture {facture_id} : {e}") from e