from datetime import datetime
from controllers.log_controller import LogController
from models.reservation_model import ReservationModel
from models.chambre_model import ChambreModel
from models.client_model import ClientModel
from controllers.facture_controller import FactureController

class ReservationController:
    def __init__(self, db_connection, user_id=None):
        self.db = db_connection
        self.user_id = user_id
        self.log_controller = LogController(self.db)

    def _log_action(self, action):
        try:
            self.log_controller.log_action(self.user_id, action)
        except Exception as e:
            print(f"Erreur log: {e}")

    def create_reservation(self, client_id, chambre_id, date_arrivee, date_depart):
        try:
            # Vérifications simples
            if not ClientModel.get_by_id(client_id):
                return {"success": False, "error": "Client inexistant."}

            chambre = ChambreModel.get_by_id(chambre_id)
            if not chambre:
                return {"success": False, "error": "Chambre inexistante."}
            if chambre['statut'] != 'libre':
                return {"success": False, "error": "Chambre occupée."}

            d_arr = datetime.strptime(date_arrivee, "%Y-%m-%d")
            d_dep = datetime.strptime(date_depart, "%Y-%m-%d")
            if d_arr >= d_dep:
                return {"success": False, "error": "Date départ doit être après date arrivée."}

            nb_nuits = (d_dep - d_arr).days
            prix_total = nb_nuits * chambre['prix_par_nuit']

            with self.db:  # Gestion transactionnelle SQLite propre
                reservation_id = ReservationModel.create(
                    client_id, chambre_id, date_arrivee, date_depart, nb_nuits, prix_total, statut="réservée")
                self.db.execute("UPDATE chambres SET statut = 'occupée' WHERE id = ?", (chambre_id,))

            self._log_action(f"Création réservation ID {reservation_id} pour client {client_id}, chambre {chambre_id}")
            return {"success": True, "reservation_id": reservation_id}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_reservation(self, reservation_id):
        try:
            res = ReservationModel.get_by_id(reservation_id)
            if not res:
                return {"success": False, "error": "Réservation non trouvée."}
            return {"success": True, "data": res}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_reservations(self, filtre=None):
        try:
            cursor = self.db.cursor()
            query = """
                SELECT r.*, c.nom AS client_nom, ch.numero AS chambre_numero
                FROM reservations r
                JOIN clients c ON r.client_id = c.id
                JOIN chambres ch ON r.chambre_id = ch.id
                WHERE r.statut NOT IN ('annulée')
            """
            params = []
            if filtre:
                if "chambre_id" in filtre:
                    query += " AND r.chambre_id = ?"
                    params.append(filtre["chambre_id"])
                if "statut" in filtre:
                    query += " AND r.statut = ?"
                    params.append(filtre["statut"])
                if "statut_not" in filtre:
                    query += " AND r.statut != ?"
                    params.append(filtre["statut_not"])

            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            reservations = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return {"success": True, "data": reservations}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_reservation(self, reservation_id, chambre_id=None, date_arrivee=None, date_depart=None):
        try:
            res = ReservationModel.get_by_id(reservation_id)
            if not res:
                return {"success": False, "error": "Réservation inexistante."}

            champs_update = {}

            # Gestion changement chambre
            if chambre_id and chambre_id != res["chambre_id"]:
                nouvelle_chambre = ChambreModel.get_by_id(chambre_id)
                if not nouvelle_chambre:
                    return {"success": False, "error": "Nouvelle chambre invalide."}
                if nouvelle_chambre["statut"] != "libre":
                    return {"success": False, "error": "Nouvelle chambre déjà occupée."}

                with self.db:
                    self.db.execute("UPDATE chambres SET statut = 'libre' WHERE id = ?", (res["chambre_id"],))
                    self.db.execute("UPDATE chambres SET statut = 'occupée' WHERE id = ?", (chambre_id,))
                champs_update["chambre_id"] = chambre_id
            else:
                chambre_id = res["chambre_id"]
                nouvelle_chambre = ChambreModel.get_by_id(chambre_id)

            # Dates
            date_arrivee = date_arrivee or res["date_arrivee"]
            date_depart = date_depart or res["date_depart"]
            d_arr = datetime.strptime(date_arrivee, "%Y-%m-%d")
            d_dep = datetime.strptime(date_depart, "%Y-%m-%d")
            if d_arr >= d_dep:
                return {"success": False, "error": "Date départ doit être après date arrivée."}

            nb_nuits = (d_dep - d_arr).days
            prix_total = nb_nuits * nouvelle_chambre["prix_par_nuit"]

            champs_update.update({
                "date_arrivee": date_arrivee,
                "date_depart": date_depart,
                "nb_nuits": nb_nuits,
                "prix_total_nuitee": prix_total
            })

            success = ReservationModel.update(reservation_id, **champs_update)
            if not success:
                return {"success": False, "error": "Mise à jour échouée."}

            self._log_action(f"Modification réservation ID {reservation_id} - {champs_update}")
            return {"success": True, "message": "Réservation mise à jour avec succès."}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_reservation(self, reservation_id):
        try:
            res = ReservationModel.get_by_id(reservation_id)
            if not res:
                return {"success": False, "error": "Réservation inexistante."}

            if res.get("statut") != "réservée":
                return {"success": False,
                        "error": f"Seules les réservations avec le statut 'réservée' peuvent être annulées. Statut actuel : {res.get('statut')}"}

            with self.db:
                ReservationModel.update(reservation_id, statut='annulée')
                self.db.execute("UPDATE chambres SET statut = 'libre' WHERE id = ?", (res['chambre_id'],))

            self._log_action(f"Annulation réservation ID {reservation_id}")
            return {"success": True, "message": "Réservation annulée avec succès."}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def checkin_reservation(self, reservation_id):
        try:
            res = ReservationModel.get_by_id(reservation_id)
            if not res:
                return {"success": False, "error": "Réservation non trouvée."}

            if res["statut"] not in ["confirmée", "réservée"]:
                return {"success": False, "error": "Réservation non valide pour le check-in."}

            chambre = ChambreModel.get_by_id(res["chambre_id"])
            if not chambre:
                return {"success": False, "error": "Chambre liée introuvable."}

            with self.db:
                ReservationModel.update(reservation_id, statut="en cours")
                self.db.execute("UPDATE chambres SET statut = 'occupée' WHERE id = ?", (chambre["id"],))

            self._log_action(f"Check-in effectué pour réservation ID {reservation_id}")
            return {"success": True, "message": "Check-in réussi."}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def checkout_reservation(self, reservation_id, methode_paiement, montant_consommation=0.0):
        try:
            res = ReservationModel.get_by_id(reservation_id)
            if not res:
                return {"success": False, "error": "Réservation non trouvée."}

            chambre = ChambreModel.get_by_id(res["chambre_id"])
            if not chambre:
                return {"success": False, "error": "Chambre introuvable."}

            montant_nuitee = res["nb_nuits"] * chambre["prix_par_nuit"]
            montant_total = montant_nuitee + montant_consommation

            FactureController.create_facture(
                reservation_id,
                montant_nuitee,
                montant_consommation,
                montant_total,
                methode_paiement
            )

            with self.db:
                ReservationModel.update(reservation_id, statut="terminée")
                self.db.execute("UPDATE chambres SET statut = 'libre' WHERE id = ?", (res["chambre_id"],))

            self._log_action(
                f"Check-out réservation ID {reservation_id}, paiement: {methode_paiement}, total: {montant_total}")
            return {"success": True, "message": "Check-out effectué avec succès, facture générée."}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_conflit(self, chambre_id, date_arrivee, date_depart):
        # Retourne True si conflit, False sinon
        resas = ReservationModel.list({
            "chambre_id": chambre_id,
            "statuts": ["réservée", "en cours"]  # uniquement les statuts qui bloquent
        })
        d_arr = datetime.strptime(date_arrivee, "%Y-%m-%d")
        d_dep = datetime.strptime(date_depart, "%Y-%m-%d")
        for r in resas:
            r_arr = datetime.strptime(r["date_arrivee"], "%Y-%m-%d")
            r_dep = datetime.strptime(r["date_depart"], "%Y-%m-%d")
            if not (d_dep <= r_arr or d_arr >= r_dep):  # chevauchement
                print(f"⚠️ Conflit détecté avec réservation ID {r['id']} ({r_arr} à {r_dep})")
                return True
        return False

    @staticmethod
    def get_by_id(reservation_id):
        return ReservationModel.get_by_id(reservation_id)

