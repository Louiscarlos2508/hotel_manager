from models.base_model import BaseModel
from datetime import datetime

class PaiementModel(BaseModel):

    @classmethod
    def create(cls, facture_id, montant, methode, date_paiement=None):
        conn = cls.connect()
        cur = conn.cursor()
        try:
            if date_paiement is None:
                date_paiement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(date_paiement, datetime):
                date_paiement = date_paiement.strftime("%Y-%m-%d %H:%M:%S")

            cur.execute("""
                INSERT INTO paiements (facture_id, montant, methode, date_paiement)
                VALUES (?, ?, ?, ?)
            """, (facture_id, montant, methode, date_paiement))
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @classmethod
    def get_by_facture(cls, facture_id):
        conn = cls.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, facture_id, montant, methode, date_paiement
                FROM paiements WHERE facture_id = ?
                ORDER BY date_paiement DESC
            """, (facture_id,))
            rows = cur.fetchall()
            return [
                {
                    "id": row[0],
                    "facture_id": row[1],
                    "montant": row[2],
                    "methode": row[3],
                    "date_paiement": row[4],
                } for row in rows
            ]
        finally:
            conn.close()

    @classmethod
    def delete(cls, paiement_id):
        conn = cls.connect()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM paiements WHERE id = ?", (paiement_id,))
            conn.commit()
            return cur.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
