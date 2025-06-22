from models.base_model import BaseModel


class ChambreModel(BaseModel):

    @classmethod
    def create(cls, numero, type_id, statut='libre'):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO chambres (numero, type_id, statut)
                VALUES (?, ?, ?)
            """, (numero, type_id, statut))
            conn.commit()
            last_id = cur.lastrowid
            conn.close()
            return last_id
        except Exception as e:
            raise Exception(f"Erreur création chambre : {e}")

    @classmethod
    def get_all(cls):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                SELECT chambres.id, numero, type_id, statut, types_chambre.nom AS type_nom, types_chambre.prix_par_nuit
                FROM chambres
                JOIN types_chambre ON chambres.type_id = types_chambre.id
            """)
            rows = cur.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Erreur récupération chambres : {e}")


    @classmethod
    def get_by_id(cls, chambre_id):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                SELECT chambres.id, numero, type_id, statut, types_chambre.nom AS type_nom, types_chambre.prix_par_nuit
                FROM chambres
                JOIN types_chambre ON chambres.type_id = types_chambre.id
                WHERE chambres.id = ?
            """, (chambre_id,))
            row = cur.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            raise Exception(f"Erreur récupération chambre : {e}")

    @classmethod
    def update(cls, chambre_id, numero, type_id, statut):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                UPDATE chambres
                SET numero = ?, type_id = ?, statut = ?
                WHERE id = ?
            """, (numero, type_id, statut, chambre_id))
            conn.commit()
            conn.close()
            return cur.rowcount  # Nombre de lignes affectées
        except Exception as e:
            raise Exception(f"Erreur mise à jour chambre : {e}")

    @classmethod
    def delete(cls, chambre_id):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM chambres WHERE id = ?", (chambre_id,))
            conn.commit()
            conn.close()
            return cur.rowcount
        except Exception as e:
            raise Exception(f"Erreur suppression chambre : {e}")
