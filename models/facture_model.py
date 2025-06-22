from models.base_model import BaseModel

class FactureModel(BaseModel):

    @classmethod
    def create(cls, reservation_id, montant_nuitee, montant_consommation, montant_total, methode_paiement):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO factures (
                reservation_id, montant_nuitee, montant_consommation,
                montant_total, methode_paiement
            ) VALUES (?, ?, ?, ?, ?)
        """, (reservation_id, montant_nuitee, montant_consommation, montant_total, methode_paiement))
        conn.commit()
        conn.close()

    @classmethod
    def get_by_reservation(cls, reservation_id):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM factures WHERE reservation_id = ?", (reservation_id,))
        row = cur.fetchone()
        conn.close()
        return row

    @classmethod
    def update_statut_paiement(cls, facture_id, nouveau_statut):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("""
            UPDATE factures SET statut_paiement = ?
            WHERE id = ?
        """, (nouveau_statut, facture_id))
        conn.commit()
        updated = cur.rowcount
        conn.close()
        return updated > 0

    @classmethod
    def delete(cls, facture_id):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM factures WHERE id = ?", (facture_id,))
        conn.commit()
        deleted = cur.rowcount
        conn.close()
        return deleted > 0
