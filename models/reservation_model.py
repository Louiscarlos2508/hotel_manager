# /home/soutonnoma/PycharmProjects/HotelManager/models/reservation_model.py
from datetime import datetime, timezone

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

            timestamp = datetime.now(timezone.utc).isoformat()
            cur.execute("UPDATE chambres SET statut = 'occupée', updated_at = ? WHERE id = ? AND is_deleted = 0", (timestamp, chambre_id,))
            conn.commit()
            return reservation_id


    @classmethod
    def perform_checkin(cls, reservation_id: int) -> bool:
        """Passe une réservation en statut 'check-in'."""
        timestamp = datetime.now(timezone.utc).isoformat()
        with cls.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE reservations SET statut = 'check-in', updated_at = ? WHERE id = ? AND is_deleted = 0",
                (timestamp, reservation_id)
            )
            conn.commit()
            return cur.rowcount > 0

    @classmethod
    def perform_cancel(cls, reservation_id: int) -> bool:
        """Annule une réservation et libère la chambre."""
        timestamp = datetime.now(timezone.utc).isoformat()
        with cls.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT chambre_id FROM reservations WHERE id = ? AND is_deleted = 0", (reservation_id,))
            resa = cur.fetchone()
            if not resa:
                return False

            chambre_id = resa["chambre_id"]
            cur.execute(
                "UPDATE reservations SET statut = 'annulée', updated_at = ? WHERE id = ? AND is_deleted = 0",
                (timestamp, reservation_id)
            )
            cur.execute(
                "UPDATE chambres SET statut = 'libre', updated_at = ? WHERE id = ? AND is_deleted = 0",
                (timestamp, chambre_id)
            )
            conn.commit()
            return True

    @classmethod
    def perform_checkout(cls, reservation_id: int, chambre_id: int, date_depart_reelle: str) -> bool:
        """
        Effectue le check-out :
        - met à jour la date de départ réelle et le statut de la réservation
        - libère la chambre
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        with cls.connect() as conn:
            cur = conn.cursor()

            cur.execute("""
                UPDATE reservations
                SET statut = 'check-out', date_depart = ?, updated_at = ?
                WHERE id = ? AND is_deleted = 0
            """, (date_depart_reelle, timestamp, reservation_id))

            cur.execute(
                "UPDATE chambres SET statut = 'libre', updated_at = ? WHERE id = ? AND is_deleted = 0",
                (timestamp, chambre_id)
            )

            conn.commit()
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
                WHERE r.is_deleted = 0
                ORDER BY r.date_arrivee DESC
            """)
            return [dict(row) for row in cur.fetchall()]

    @classmethod
    def get_by_id(cls, reservation_id):
        with cls.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM reservations WHERE id = ? AND is_deleted = 0", (reservation_id,))
            row = cur.fetchone()
            return dict(row) if row else None


    @classmethod
    def update(cls, reservation_id, **kwargs):
        if not kwargs:
            return False

        timestamp = datetime.now(timezone.utc).isoformat()

        with cls.connect() as conn:
            cur = conn.cursor()

            if "chambre_id" in kwargs:
                cur.execute("SELECT chambre_id FROM reservations WHERE id = ? AND is_deleted = 0", (reservation_id,))
                row = cur.fetchone()
                if not row:
                    return False
                ancienne_chambre_id = row["chambre_id"]
                nouvelle_chambre_id = kwargs["chambre_id"]

                if ancienne_chambre_id != nouvelle_chambre_id:
                    cur.execute("UPDATE chambres SET statut = 'libre', updated_at = ? WHERE id = ? AND is_deleted = 0",
                                (timestamp, ancienne_chambre_id))
                    cur.execute("UPDATE chambres SET statut = 'occupée', updated_at = ? WHERE id = ? AND is_deleted = 0",
                                (timestamp, nouvelle_chambre_id))

            # Construction de la requête dynamique
            fields = ", ".join([f"{key} = ?" for key in kwargs])
            query = f"UPDATE reservations SET {fields}, updated_at = ? WHERE id = ? AND is_deleted = 0"
            params = list(kwargs.values()) + [timestamp, reservation_id]

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
                WHERE 1=1 AND r.is_deleted = 0
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