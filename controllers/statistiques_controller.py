from models.base_model import BaseModel
import logging

class StatistiquesController(BaseModel):

    @classmethod
    def get_nombre_reservations_par_mois(cls, annee):
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT strftime('%m', date_arrivee) AS mois, COUNT(*) 
                    FROM reservations 
                    WHERE strftime('%Y', date_arrivee) = ? 
                    GROUP BY mois
                """, (str(annee),))
                rows = cur.fetchall()

            result = {int(mois): count for mois, count in rows}
            # Compléter avec 0 pour mois absents
            return {m: result.get(m, 0) for m in range(1, 13)}
        except Exception as e:
            logging.error(f"Erreur get_nombre_reservations_par_mois: {e}")
            return {m: 0 for m in range(1, 13)}

    @classmethod
    def get_revenu_total_par_mois(cls, annee):
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT strftime('%m', date_facture) AS mois, SUM(montant_total)
                    FROM factures
                    WHERE strftime('%Y', date_facture) = ? AND statut_paiement = 'payé'
                    GROUP BY mois
                """, (str(annee),))
                rows = cur.fetchall()

            result = {int(mois): total if total is not None else 0 for mois, total in rows}
            return {m: result.get(m, 0) for m in range(1, 13)}
        except Exception as e:
            logging.error(f"Erreur get_revenu_total_par_mois: {e}")
            return {m: 0 for m in range(1, 13)}

    @classmethod
    def get_occupations_chambres(cls):
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT statut, COUNT(*) FROM chambres GROUP BY statut")
                rows = cur.fetchall()

            result = {statut: count for statut, count in rows}
            # Assurer toutes les clés
            return {
                'libre': result.get('libre', 0),
                'occupée': result.get('occupée', 0),
                'en maintenance': result.get('en maintenance', 0)
            }
        except Exception as e:
            logging.error(f"Erreur get_occupations_chambres: {e}")
            return {'libre': 0, 'occupée': 0, 'en maintenance': 0}

    @classmethod
    def get_top_types_chambres(cls, limit=5):
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT tc.id, tc.nom, COUNT(r.id) AS nb_reservations
                    FROM types_chambre tc
                    LEFT JOIN chambres c ON c.type_id = tc.id
                    LEFT JOIN reservations r ON r.chambre_id = c.id
                    GROUP BY tc.id, tc.nom
                    ORDER BY nb_reservations DESC
                    LIMIT ?
                """, (limit,))
                rows = cur.fetchall()

            return [{'id': r[0], 'nom': r[1], 'nb_reservations': r[2]} for r in rows]
        except Exception as e:
            logging.error(f"Erreur get_top_types_chambres: {e}")
            return []

    @classmethod
    def get_clients_frequents(cls, limit=5):
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT c.id, c.nom, c.prenom, COUNT(r.id) AS nb_reservations
                    FROM clients c
                    LEFT JOIN reservations r ON r.client_id = c.id
                    GROUP BY c.id, c.nom, c.prenom
                    ORDER BY nb_reservations DESC
                    LIMIT ?
                """, (limit,))
                rows = cur.fetchall()

            return [{'id': r[0], 'nom': r[1], 'prenom': r[2], 'nb_reservations': r[3]} for r in rows]
        except Exception as e:
            logging.error(f"Erreur get_clients_frequents: {e}")
            return []
