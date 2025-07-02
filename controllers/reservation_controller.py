# /home/soutonnoma/PycharmProjects/HotelManager/controllers/reservation_controller.py

from datetime import datetime, date
from models.reservation_model import ReservationModel
from models.chambre_model import ChambreModel
from models.client_model import ClientModel
from controllers.facture_controller import FactureController
from controllers.log_controller import LogController

class ReservationController:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.logger = LogController(user_id)

    def create(self, client_id, chambre_id, date_arrivee, date_depart, nb_adultes=1, nb_enfants=0):
        """Valide les données métier et délègue la création complète au modèle."""
        try:
            chambre = ChambreModel.get_by_id(chambre_id)
            if not chambre or chambre['statut'] != 'libre':
                return {"success": False, "error": "Chambre non disponible ou introuvable."}

            client = ClientModel.get_by_id(client_id)
            if not client:
                return {"success": False, "error": "Client introuvable."}

            d_arr = datetime.strptime(date_arrivee, "%Y-%m-%d").date()
            d_dep = datetime.strptime(date_depart, "%Y-%m-%d").date()
            nb_nuits = max(1, (d_dep - d_arr).days)
            prix_total_estime = nb_nuits * chambre['prix_par_nuit']

            # Appel UNIQUE au modèle pour toute l'opération
            reservation_id = ReservationModel.create_full_reservation(
                client_id, chambre_id, date_arrivee, date_depart,
                nb_adultes, nb_enfants, prix_total_estime
            )
            self.logger.log_action("Création réservation", f"ID {reservation_id}")
            return {"success": True, "reservation_id": reservation_id}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la création de la réservation : {e}"}

    def checkin(self, reservation_id):
        """Gère la logique métier du check-in et délègue l'action à la base de données."""
        try:
            resa = ReservationModel.get_by_id(reservation_id)
            if not resa or resa['statut'] != 'réservée':
                return {"success": False, "error": "Réservation invalide pour check-in."}

            if ReservationModel.perform_checkin(reservation_id):
                self.logger.log_action("Check-in", f"Réservation {reservation_id}")
                return {"success": True}
            else:
                return {"success": False, "error": "Le check-in a échoué en base de données."}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors du check-in : {e}"}

    def cancel(self, reservation_id):
        """Gère la logique métier de l'annulation et délègue l'action à la base de données."""
        try:
            resa = ReservationModel.get_by_id(reservation_id)
            if not resa or resa['statut'] != 'réservée':
                return {"success": False, "error": "Impossible d'annuler cette réservation (statut incorrect)."}

            if ReservationModel.perform_cancel(reservation_id):
                self.logger.log_action("Annulation", f"Réservation {reservation_id}")
                return {"success": True}
            else:
                return {"success": False, "error": "L'annulation a échoué en base de données."}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'annulation : {e}"}

    @staticmethod
    def checkout(reservation_id, user_id=None):
        """
        Gère la logique métier du check-out.
        1. Valide la réservation.
        2. Vérifie que la facture est entièrement payée.
        3. Met à jour le statut de la réservation et de la chambre.
        """
        try:
            # 1. Valider la réservation
            resa = ReservationModel.get_by_id(reservation_id)
            if not resa or resa['statut'] != 'check-in':
                return {"success": False, "error": "Impossible de faire le check-out (statut incorrect)."}

            # 2. Vérifier que la facture est soldée
            facture_resp = FactureController.get_facture_par_reservation(reservation_id)
            if not facture_resp.get("success") or not facture_resp.get("data"):
                return {"success": False, "error": "Facture introuvable pour la vérification."}

            facture = facture_resp["data"]
            total_a_payer = facture.get("montant_total_ttc", 0)
            deja_paye = facture.get("montant_paye", 0)

            if deja_paye < total_a_payer:
                return {"success": False,
                        "error": f"Paiement insuffisant. Reste à payer : {total_a_payer - deja_paye:,.0f} FCFA."}

            # 3. Mettre à jour la réservation et la chambre via le modèle
            date_dep_reelle = date.today().strftime("%Y-%m-%d")
            if ReservationModel.perform_checkout(reservation_id, resa['chambre_id'], date_dep_reelle):
                FactureController.mettre_a_jour_statut(facture['id'], 'Payée')
                logger = LogController(user_id)
                logger.log_action("Check-out", f"Réservation {reservation_id}")
                return {"success": True, "message": "Check-out réussi."}
            else:
                return {"success": False, "error": "La mise à jour de la réservation a échoué."}

        except Exception as e:
            return {"success": False, "error": f"Erreur lors du check-out : {e}"}




    def update(self, reservation_id, **kwargs):
            """Valide et demande la mise à jour d'une réservation."""
            try:
                # Ici, on peut ajouter des validations métier si nécessaire
                if ReservationModel.update(reservation_id, **kwargs):
                    self.logger.log_action("Modification réservation", f"ID {reservation_id}")
                    return {"success": True}
                else:
                    return {"success": False, "error": "Aucune modification effectuée."}
            except Exception as e:
                return {"success": False, "error": str(e)}

    # --- Les méthodes statiques et de lecture n'ont pas besoin de changer ---
    @staticmethod
    def list_reservations(filtre=None):
        try:
            if filtre:
                # Utiliser la méthode list du model qui supporte filtre
                data = ReservationModel.list(filtre)
            else:
                data = ReservationModel.get_all()
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_by_id(reservation_id):
        try:
            resa = ReservationModel.get_by_id(reservation_id)
            if not resa:
                return {"success": False, "error": "Non trouvé"}
            return {"success": True, "data": resa}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def check_conflit(chambre_id, date_arrivee, date_depart, exclude_id=None):
        resas = ReservationModel.list({"chambre_id": chambre_id, "statuts": ["réservée", "check-in"]})
        d_arr = datetime.strptime(date_arrivee, "%Y-%m-%d").date()
        d_dep = datetime.strptime(date_depart, "%Y-%m-%d").date()
        for r in resas:
            if exclude_id and r["id"] == exclude_id:
                continue
            r_arr = datetime.strptime(r["date_arrivee"], "%Y-%m-%d").date()
            r_dep = datetime.strptime(r["date_depart"], "%Y-%m-%d").date()
            # Logique de chevauchement
            if not (d_dep <= r_arr or d_arr >= r_dep):
                return True
        return False