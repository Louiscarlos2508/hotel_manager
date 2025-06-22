from models.base_model import BaseModel
import hashlib

class UserModel(BaseModel):

    @classmethod
    def get_by_username(cls, username):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        return row

    @classmethod
    def get_all(cls):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, username, nom_complet, role, actif FROM users")
        rows = cur.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "username": row[1],
                "nom_complet": row[2],
                "role": row[3],
                "actif": bool(row[4])
            }
            for row in rows
        ]

    @classmethod
    def create(cls, username, password, role, nom_complet=None, actif=True):
        """Crée un nouvel utilisateur avec hashage du mot de passe"""
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        conn = cls.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (username, password_hash, role, nom_complet, actif)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, role, nom_complet, int(actif)))
            conn.commit()
        except Exception as e:
            print(f"Erreur création utilisateur: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def update_password(cls, user_id, new_password):
        """Met à jour le mot de passe d'un utilisateur"""
        password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        conn = cls.connect()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
            conn.commit()
        except Exception as e:
            print(f"Erreur mise à jour mot de passe: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def set_active_status(cls, user_id, actif):
        """Active ou désactive un utilisateur"""
        conn = cls.connect()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE users SET actif = ? WHERE id = ?", (int(actif), user_id))
            conn.commit()
        except Exception as e:
            print(f"Erreur changement statut actif: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def update_user(cls, user_id, nom_complet, role, actif):
        conn = cls.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE users SET nom_complet = ?, role = ?, actif = ? WHERE id = ?
            """, (nom_complet, role, int(actif), user_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def delete_user(cls, user_id):
        conn = cls.connect()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
