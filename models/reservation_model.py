# /home/soutonnoma/PycharmProjects/HotelManger/models/reservation_model.py

from models.base_model import BaseModel


class ReservationModel(BaseModel):

    # La méthode _ensure_connection n'est plus nécessaire, on la supprime.

    @classmethod
    def create_full_reservation(cls, client_id, chambre_id, date_arrivee, date_depart,
                                nb_adultes, nb_enfants, prix_total_nuitee_estime):
        """
        Crée une réservation et met à jour la chambre dans une transaction unique.
        """
        # Utilisation du nouveau pattern de connexion
        with cls.connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO reservations (client_id, chambre_id, date_arrivee, date_depart, nb_adultes, nb_enfants, prix_total_nuitee_estime, statut)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'réservée')
            """, (client_id, chambre_id, date_arrivee, date_depart, nb_adultes, nb_enfants, prix_total_nuitee_estime))
            reservation_id = cur.lastrowid

            cur.execute("UPDATE chambres SET statut = 'occupée' WHERE id = ?", (chambre_id,))
            conn.commit()
            return reservation_id

    @classmethod
    def perform_checkin(cls, reservation_id: int) -> bool:
        with cls.connect() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE reservations SET statut = 'check-in' WHERE id = ?", (reservation_id,))
            conn.commit()
            return cur.rowcount > 0

    @classmethod
    def perform_cancel(cls, reservation_id: int) -> bool:
        with cls.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT chambre_id FROM reservations WHERE id = ?", (reservation_id,))
            resa = cur.fetchone()
            if not resa:
                return False

            cur.execute("UPDATE reservations SET statut = 'annulée' WHERE id = ?", (reservation_id,))
            cur.execute("UPDATE chambres SET statut = 'libre' WHERE id = ?", (resa['chambre_id'],))
            conn.commit()
            return cur.rowcount > 0

    @classmethod
    def perform_checkout(cls, reservation_id: int, chambre_id: int, date_depart_reelle: str) -> bool:
        """
        Met à jour le statut de la réservation et de la chambre lors du check-out.
        Le montant final est géré par la facture.
        """
        with cls.connect() as conn:
            cur = conn.cursor()
            # --- MODIFICATION : On ne met plus à jour le prix ici ---
            cur.execute("""
                    UPDATE reservations 
                    SET statut = 'check-out', date_depart = ?
                    WHERE id = ?
                """, (date_depart_reelle, reservation_id))
            cur.execute("UPDATE chambres SET statut = 'libre' WHERE id = ?", (chambre_id,))
            conn.commit()
            # On vérifie que la réservation a bien été modifiée
            return cur.rowcount > 0

    @classmethod
    def get_all(cls):
        with cls.connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.id, c.nom || ' ' || c.prenom AS client, ch.numero AS chambre,
                       r.date_arrivee, r.date_depart, r.statut,
                       r.client_id, r.chambre_id,
                       r.nb_adultes, r.nb_enfants, r.prix_total_nuitee_estime
                FROM reservations r
                JOIN clients c ON r.client_id = c.id
                JOIN chambres ch ON r.chambre_id = ch.id
                ORDER BY r.date_arrivee DESC
            """)
            return [dict(row) for row in cur.fetchall()]

    @classmethod
    def get_by_id(cls, reservation_id):
        with cls.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM reservations WHERE id = ?", (reservation_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    @classmethod
    def update(cls, reservation_id, **kwargs):
        if not kwargs:
            return False

        with cls.connect() as conn:
            cur = conn.cursor()
            if "chambre_id" in kwargs:
                cur.execute("SELECT chambre_id FROM reservations WHERE id = ?", (reservation_id,))
                row = cur.fetchone()
                if not row: return False
                ancienne_chambre_id = row['chambre_id']
                nouvelle_chambre_id = kwargs["chambre_id"]
                if ancienne_chambre_id != nouvelle_chambre_id:
                    cur.execute("UPDATE chambres SET statut = 'libre' WHERE id = ?", (ancienne_chambre_id,))
                    cur.execute("UPDATE chambres SET statut = 'occupée' WHERE id = ?", (nouvelle_chambre_id,))

            fields = ", ".join([f"{key} = ?" for key in kwargs])
            params = list(kwargs.values())
            params.append(reservation_id)
            query = f"UPDATE reservations SET {fields} WHERE id = ?"
            cur.execute(query, tuple(params))
            conn.commit()
            return cur.rowcount > 0

    @classmethod
    def list(cls, filtre=None):
        with cls.connect() as conn:
            query = """
                SELECT r.id, c.nom || ' ' || c.prenom AS client, ch.numero AS chambre,
                       r.date_arrivee, r.date_depart, r.statut, r.client_id, r.chambre_id
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
                    params.extend(filtre["statuts"])
                if "date_depart" in filtre:
                    query += " AND r.date_depart = ?"
                    params.append(filtre["date_depart"])

            query += " ORDER BY r.date_arrivee DESC"
            cur = conn.cursor()
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]