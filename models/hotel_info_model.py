from models.base_model import BaseModel

class HotelInfoModel(BaseModel):

    @classmethod
    def get_info(cls):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("SELECT nom, adresse, telephone, email, siret FROM hotel_info WHERE id = 1")
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                "nom": row[0],
                "adresse": row[1],
                "telephone": row[2],
                "email": row[3],
                "siret": row[4],
            }
        return None

    @classmethod
    def save_info(cls, nom, adresse, telephone, email, siret):
        conn = cls.connect()
        cur = conn.cursor()
        # Vérifie si ligne existe
        cur.execute("SELECT id FROM hotel_info WHERE id = 1")
        exists = cur.fetchone()
        if exists:
            # Update
            cur.execute("""
                UPDATE hotel_info
                SET nom = ?, adresse = ?, telephone = ?, email = ?, siret = ?
                WHERE id = 1
            """, (nom, adresse, telephone, email, siret))
        else:
            # Insert
            cur.execute("""
                INSERT INTO hotel_info (id, nom, adresse, telephone, email, siret)
                VALUES (1, ?, ?, ?, ?, ?)
            """, (nom, adresse, telephone, email, siret))
        conn.commit()
        conn.close()
