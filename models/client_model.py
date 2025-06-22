import sqlite3
from models.base_model import BaseModel

class ClientModel(BaseModel):

    @classmethod
    def connect(cls):
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def create(cls, nom, prenom=None, tel=None, email=None, cni=None, adresse=None):
        conn = cls.connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO clients (nom, prenom, tel, email, cni, adresse)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                nom.strip() if isinstance(nom, str) else nom,
                prenom.strip() if isinstance(prenom, str) and prenom is not None else prenom,
                tel.strip() if isinstance(tel, str) and tel is not None else tel,
                email.strip() if isinstance(email, str) and email is not None else email,
                cni.strip() if isinstance(cni, str) and cni is not None else cni,
                adresse.strip() if isinstance(adresse, str) and adresse is not None else adresse,
            ))
            conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Erreur création client : {e}")
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, client_id):
        conn = cls.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
            else:
                return None
        finally:
            conn.close()

    @classmethod
    def get_all(cls):
        conn = cls.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clients")
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def update(cls, client_id, nom=None, prenom=None, tel=None, email=None, cni=None, adresse=None):
        conn = cls.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            if not cur.fetchone():
                return 0  # client non trouvé

            fields = []
            values = []
            if nom is not None:
                fields.append("nom = ?")
                values.append(nom.strip() if isinstance(nom, str) else nom)
            if prenom is not None:
                fields.append("prenom = ?")
                values.append(prenom.strip() if isinstance(prenom, str) else prenom)
            if tel is not None:
                fields.append("tel = ?")
                values.append(tel.strip() if isinstance(tel, str) else tel)
            if email is not None:
                fields.append("email = ?")
                values.append(email.strip() if isinstance(email, str) else email)
            if cni is not None:
                fields.append("cni = ?")
                values.append(cni.strip() if isinstance(cni, str) else cni)
            if adresse is not None:
                fields.append("adresse = ?")
                values.append(adresse.strip() if isinstance(adresse, str) else adresse)

            if not fields:
                return 0  # rien à mettre à jour

            values.append(client_id)
            sql = f"UPDATE clients SET {', '.join(fields)} WHERE id = ?"
            cur.execute(sql, tuple(values))
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    @classmethod
    def delete(cls, client_id):
        if cls.has_reservations(client_id):
            # Ne supprime pas, client lié à au moins une réservation
            return 0
        conn = cls.connect()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    @classmethod
    def has_reservations(cls, client_id):
        conn = cls.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM reservations WHERE client_id = ?", (client_id,))
            count = cur.fetchone()[0]
            return count > 0
        finally:
            conn.close()

    @classmethod
    def get_all_with_reservation_count(cls):
        conn = cls.connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                    SELECT clients.*, 
                           COUNT(reservations.id) AS nb_reservations
                    FROM clients
                    LEFT JOIN reservations ON clients.id = reservations.client_id
                    GROUP BY clients.id
                    ORDER BY clients.nom
                """)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
