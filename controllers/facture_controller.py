from datetime import datetime

from models.facture_model import FactureModel


class FactureController:

    @staticmethod
    def create_facture(reservation_id, montant_nuitee, montant_consommation, montant_total, methode_paiement):
        if not reservation_id:
            raise ValueError("L'ID de réservation est obligatoire.")
        if montant_nuitee < 0 or montant_consommation < 0 or montant_total < 0:
            raise ValueError("Les montants ne peuvent pas être négatifs.")
        if montant_total < (montant_nuitee + montant_consommation):
            raise ValueError("Le montant total doit être au moins la somme des montants de nuitée et consommation.")
        if not methode_paiement:
            raise ValueError("La méthode de paiement est obligatoire.")

        try:
            FactureModel.create(
                reservation_id,
                montant_nuitee,
                montant_consommation,
                montant_total,
                methode_paiement
            )
            return True
        except Exception as e:
            # Log l'erreur si tu as un système de logs, sinon raise
            raise Exception(f"Erreur lors de la création de la facture : {e}")

    @staticmethod
    def get_facture_by_reservation(reservation_id):
        if not reservation_id:
            raise ValueError("L'ID de réservation est obligatoire.")

        facture = FactureModel.get_by_reservation(reservation_id)
        if not facture:
            return None
        return facture

    @staticmethod
    def update_statut_paiement(facture_id, nouveau_statut):
        if not facture_id:
            raise ValueError("L'ID de facture est obligatoire.")
        if nouveau_statut not in ['non payé', 'payé', 'partiellement payé']:
            raise ValueError("Statut de paiement invalide.")

        try:
            success = FactureModel.update_statut_paiement(facture_id, nouveau_statut)
            if not success:
                raise Exception("Mise à jour du statut échouée.")
            return True
        except Exception as e:
            raise Exception(f"Erreur lors de la mise à jour du statut de paiement : {e}")

    @staticmethod
    def delete_facture(facture_id):
        if not facture_id:
            raise ValueError("L'ID de facture est obligatoire.")
        try:
            success = FactureModel.delete(facture_id)
            if not success:
                raise Exception("Suppression de la facture échouée.")
            return True
        except Exception as e:
            raise Exception(f"Erreur lors de la suppression de la facture : {e}")

    @staticmethod
    def create_facture_auto(reservation_id):
        if not reservation_id:
            return {"success": False, "error": "ID réservation manquant."}
        try:
            from controllers.reservation_controller import ReservationController
            from controllers.chambre_controller import ChambreController
            from controllers.consommation_controller import ConsommationController

            reservation_ctrl = ReservationController(reservation_id)
            chambre_ctrl = ChambreController()

            res_resp = reservation_ctrl.get_reservation(reservation_id)
            if not res_resp["success"]:
                return {"success": False, "error": "Réservation introuvable."}
            reservation = res_resp["data"]

            chambre_resp = chambre_ctrl.get_chambre_by_id(reservation["chambre_id"])
            if not chambre_resp["success"]:
                return {"success": False, "error": "Chambre introuvable."}
            chambre = chambre_resp["data"]

            prix_par_nuit = chambre["prix_par_nuit"]
            date_arrivee = datetime.fromisoformat(reservation["date_arrivee"]).date()
            date_depart = datetime.fromisoformat(reservation["date_depart"]).date()

            nb_nuits = (date_depart - date_arrivee).days
            if nb_nuits <= 0:
                nb_nuits = 1

            montant_nuitee = nb_nuits * prix_par_nuit

            cons_resp = ConsommationController.get_consommations_by_reservation(reservation_id)
            total_consommation = 0
            if cons_resp.get("success", False):
                total_consommation = sum(c["quantite"] * c["prix_unitaire"] for c in cons_resp["data"])

            montant_total = montant_nuitee + total_consommation

            # Crée la facture (ajoute méthode paiement = None)
            FactureModel.create(
                reservation_id=reservation_id,
                montant_nuitee=montant_nuitee,
                montant_consommation=total_consommation,
                montant_total=montant_total,
                methode_paiement=None
            )

            facture = FactureModel.get_by_reservation(reservation_id)
            return {"success": True, "data": dict(facture) if facture else None}

        except Exception as e:
            return {"success": False, "error": str(e)}
