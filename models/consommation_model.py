from models.base_model import BaseModel

class ConsommationModel(BaseModel):

    @classmethod
    def create(cls, reservation_id, designation, quantite=1, prix_unitaire=0.0):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO consommations (reservation_id, designation, quantite, prix_unitaire)
                VALUES (?, ?, ?, ?)
            """, (reservation_id, designation, quantite, prix_unitaire))
            conn.commit()
            return cur.lastrowid  # retourne l'id créé
        except Exception as e:
            print(f"Erreur lors de la création de consommation : {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_by_reservation(cls, reservation_id=None):
        try:
            conn = cls.connect()
            cur = conn.cursor()

            if reservation_id is None:
                cur.execute("""
                    SELECT id, reservation_id, designation, quantite, prix_unitaire, date
                    FROM consommations
                    ORDER BY date DESC
                """)
            else:
                cur.execute("""
                    SELECT id, reservation_id, designation, quantite, prix_unitaire, date
                    FROM consommations
                    WHERE reservation_id = ?
                    ORDER BY date DESC
                """, (reservation_id,))

            rows = cur.fetchall()
            return [dict(zip(['id', 'reservation_id', 'designation', 'quantite', 'prix_unitaire', 'date'], row)) for row
                    in rows]

        except Exception as e:
            print(f"Erreur lors de la récupération des consommations : {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def update(cls, consommation_id, reservation_id=None, designation=None, quantite=None, prix_unitaire=None):
        try:
            conn = cls.connect()
            cur = conn.cursor()

            fields = []
            params = []

            if reservation_id is not None:
                fields.append("reservation_id = ?")
                params.append(reservation_id)
            if designation is not None:
                fields.append("designation = ?")
                params.append(designation)
            if quantite is not None:
                fields.append("quantite = ?")
                params.append(quantite)
            if prix_unitaire is not None:
                fields.append("prix_unitaire = ?")
                params.append(prix_unitaire)

            if not fields:
                return False  # rien à mettre à jour

            params.append(consommation_id)

            query = f"UPDATE consommations SET {', '.join(fields)} WHERE id = ?"
            cur.execute(query, tuple(params))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Erreur lors de la mise à jour de consommation : {e}")
            return False
        finally:
            conn.close()

    @classmethod
    def delete(cls, consommation_id):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM consommations WHERE id = ?", (consommation_id,))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Erreur lors de la suppression de consommation : {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_between_dates(start_date, end_date):
        conn = BaseModel.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, reservation_id, designation, quantite, prix_unitaire, date
            FROM consommations
            WHERE date BETWEEN ? AND ?
        """, (str(start_date), str(end_date)))
        rows = cur.fetchall()
        conn.close()
        return [dict(zip(['id', 'reservation_id', 'designation', 'quantite', 'prix_unitaire', 'date'], row)) for row in
                rows]

    @classmethod
    def get_all(cls):
        try:
            conn = cls.connect()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, reservation_id, designation, quantite, prix_unitaire, date
                FROM consommations
                ORDER BY date DESC
            """)
            rows = cur.fetchall()
            return [dict(zip(['id', 'reservation_id', 'designation', 'quantite', 'prix_unitaire', 'date'], row)) for row
                    in rows]
        except Exception as e:
            print(f"Erreur get_all consommations : {e}")
            return []
        finally:
            conn.close()
