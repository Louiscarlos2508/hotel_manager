# /home/soutonnoma/PycharmProjects/HotelManger/models/hotel_info_model.py
from models.base_model import BaseModel
import sqlite3

class HotelInfoModel(BaseModel):

    @classmethod
    def get_info(cls):
        """Récupère les informations de l'hôtel, y compris TVA et TDT."""
        # --- MODIFICATION : On sélectionne les nouvelles colonnes ---
        query = "SELECT nom, adresse, telephone, email, siret, tva_hebergement, tva_restauration, tdt_par_personne FROM hotel_info WHERE id = 1"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur récupération info hôtel : {e}") from e

    @classmethod
    def save_info(cls, nom, adresse, telephone, email, siret, tva_hebergement, tva_restauration, tdt_par_personne):
        """Sauvegarde ou met à jour les informations de l'hôtel, y compris TVA et TDT."""
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                # --- MODIFICATION : On insère les nouvelles colonnes ---
                query = """
                    INSERT OR REPLACE INTO hotel_info (id, nom, adresse, telephone, email, siret, tva_hebergement, tva_restauration, tdt_par_personne)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cur.execute(query, (nom, adresse, telephone, email, siret, tva_hebergement, tva_restauration, tdt_par_personne))
                conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Erreur sauvegarde info hôtel : {e}") from e