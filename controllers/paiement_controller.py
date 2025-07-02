# /home/soutonnoma/PycharmProjects/HotelManager/controllers/paiement_controller.py
from models.paiement_model import PaiementModel
from models.facture_model import FactureModel


class PaiementController:

    @staticmethod
    def creer_paiement(facture_id, montant, methode, date_paiement=None):
        """
        Crée un paiement et met à jour le montant payé sur la facture associée.
        """
        if not facture_id or not isinstance(facture_id, int) or facture_id <= 0:
            return {"success": False, "error": "ID facture invalide."}
        if montant is None or montant <= 0:
            return {"success": False, "error": "Montant invalide."}
        if not methode or not isinstance(methode, str):
            return {"success": False, "error": "Méthode de paiement invalide."}
        try:
            # 1. Récupérer la facture pour connaître le montant déjà payé
            facture = FactureModel.get_by_id(facture_id)
            if not facture:
                return {"success": False, "error": "Facture associée introuvable."}

            # 2. Créer le nouvel enregistrement de paiement
            paiement_id = PaiementModel.create(facture_id, montant, methode, date_paiement)

            # 3. Mettre à jour le montant total payé sur la facture
            nouveau_montant_paye = facture.get('montant_paye', 0) + montant
            FactureModel.update_montants(
                facture_id,
                facture.get('montant_total_ht', 0),
                facture.get('montant_total_tva', 0),
                facture.get('montant_total_ttc', 0),
                nouveau_montant_paye
            )

            return {"success": True, "paiement_id": paiement_id, "message": "Paiement créé avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur création paiement : {e}"}

    @staticmethod
    def get_paiements_par_facture(facture_id):
        if not facture_id or not isinstance(facture_id, int) or facture_id <= 0:
            return {"success": False, "error": "ID facture invalide."}
        try:
            paiements = PaiementModel.get_by_facture(facture_id)
            return {"success": True, "data": paiements}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération paiements : {e}"}

    @staticmethod
    def get_all():
        try:
            paiements = PaiementModel.get_all()
            return {"success": True, "data": paiements}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération paiements : {e}"}