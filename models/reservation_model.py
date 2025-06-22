from models.base_model import BaseModel

class ReservationModel(BaseModel):

    @classmethod
    def create(cls, client_id, chambre_id, date_arrivee, date_depart, nb_nuits, prix_total, statut="réservée"):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reservations (client_id, chambre_id, date_arrivee, date_depart, nb_nuits, prix_total_nuitee, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (client_id, chambre_id, date_arrivee, date_depart, nb_nuits, prix_total, statut))
        conn.commit()
        last_id = cur.lastrowid
        conn.close()
        return last_id

    @classmethod
    def get_all(cls):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT r.id, c.nom || ' ' || c.prenom AS client, ch.numero AS chambre,
                   r.date_arrivee, r.date_depart, r.statut,
                   r.client_id, r.chambre_id
            FROM reservations r
            JOIN clients c ON r.client_id = c.id
            JOIN chambres ch ON r.chambre_id = ch.id
        """)
        rows = cur.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "client": row[1],
                "chambre": row[2],
                "date_arrivee": row[3],
                "date_depart": row[4],
                "statut": row[5],
                "client_id": row[6],
                "chambre_id": row[7]
            }
            for row in rows
        ]

    @classmethod
    def get_by_id(cls, reservation_id):
        conn = cls.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, client_id, chambre_id, date_arrivee, date_depart, statut, nb_nuits, prix_total_nuitee
            FROM reservations WHERE id = ?
        """, (reservation_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "client_id": row[1],
                "chambre_id": row[2],
                "date_arrivee": row[3],
                "date_depart": row[4],
                "statut": row[5],
                "nb_nuits": row[6],
                "prix_total_nuitee": row[7]
            }
        return None

    @classmethod
    def list(cls, filtre=None):
        conn = cls.connect()
        cur = conn.cursor()

        query = """
            SELECT r.id, r.client_id, r.chambre_id,
                   c.nom || ' ' || c.prenom AS client_nom,
                   ch.numero AS chambre_numero,
                   r.date_arrivee, r.date_depart, r.statut
            FROM reservations r
            JOIN clients c ON r.client_id = c.id
            JOIN chambres ch ON r.chambre_id = ch.id
            WHERE 1=1
        """
        params = []

        if filtre:
            if "chambre_id" in filtre:
                query += " AND r.chambre_id = ?"
                params.append(filtre["chambre_id"])
            if "statuts" in filtre:
                placeholders = ','.join(['?'] * len(filtre["statuts"]))
                query += f" AND r.statut IN ({placeholders})"
                params += filtre["statuts"]
            elif "statut_not" in filtre:
                query += " AND r.statut != ?"
                params.append(filtre["statut_not"])

        query += " ORDER BY r.date_arrivee DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "client_id": row[1],
                "chambre_id": row[2],
                "client_nom": row[3],
                "chambre_numero": row[4],
                "date_arrivee": row[5],
                "date_depart": row[6],
                "statut": row[7],
            }
            for row in rows
        ]

    @classmethod
    def update(cls, reservation_id, **kwargs):
        if not kwargs:
            return False
        conn = cls.connect()
        cur = conn.cursor()

        fields = []
        params = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            params.append(v)
        params.append(reservation_id)

        query = f"UPDATE reservations SET {', '.join(fields)} WHERE id = ?"
        cur.execute(query, tuple(params))
        conn.commit()
        updated = cur.rowcount > 0
        conn.close()
        return updated
