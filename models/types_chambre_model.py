from models.base_model import BaseModel

class TypesChambreModel(BaseModel):

    @classmethod
    def create(cls, nom, description, prix_par_nuit):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO types_chambre (nom, description, prix_par_nuit)
                VALUES (?, ?, ?)
            """, (nom, description, prix_par_nuit))
            conn.commit()
            last_id = cur.lastrowid
            conn.close()
            return last_id
        except Exception as e:
            raise Exception(f"Erreur création type chambre : {e}")

    @classmethod
    def get_all(cls):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nom, description, prix_par_nuit
                FROM types_chambre
                ORDER BY nom ASC
            """)
            rows = cur.fetchall()
            conn.close()
            return [
                {
                    "id": r[0],
                    "nom": r[1],
                    "description": r[2],
                    "prix_par_nuit": r[3]
                }
                for r in rows
            ]
        except Exception as e:
            raise Exception(f"Erreur récupération types de chambre : {e}")

    @classmethod
    def get_by_id(cls, type_id):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nom, description, prix_par_nuit
                FROM types_chambre
                WHERE id = ?
            """, (type_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                return {
                    "id": row[0],
                    "nom": row[1],
                    "description": row[2],
                    "prix_par_nuit": row[3]
                }
            return None
        except Exception as e:
            raise Exception(f"Erreur récupération type chambre : {e}")

    @classmethod
    def update(cls, type_id, nom, description, prix_par_nuit):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                UPDATE types_chambre
                SET nom = ?, description = ?, prix_par_nuit = ?
                WHERE id = ?
            """, (nom, description, prix_par_nuit, type_id))
            conn.commit()
            conn.close()
            return cur.rowcount
        except Exception as e:
            raise Exception(f"Erreur mise à jour type chambre : {e}")

    @classmethod
    def delete(cls, type_id):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM types_chambre WHERE id = ?", (type_id,))
            conn.commit()
            conn.close()
            return cur.rowcount
        except Exception as e:
            raise Exception(f"Erreur suppression type chambre : {e}")
