from datetime import datetime
from models.paiement_model import PaiementModel

class PaiementController:

    @staticmethod
    def enregistrer_paiement(facture_id, montant, methode, date_paiement=None):
        if not facture_id:
            raise ValueError("L'ID de facture est obligatoire.")
        if montant <= 0:
            raise ValueError("Le montant doit être strictement positif.")
        if not methode or methode.strip() == "":
            raise ValueError("La méthode de paiement est obligatoire.")

        if date_paiement is not None:
            if isinstance(date_paiement, str):
                # On peut tenter un parse ISO
                try:
                    datetime.fromisoformat(date_paiement)
                except ValueError:
                    raise ValueError("La date de paiement doit être au format ISO 'YYYY-MM-DD' ou un datetime valide.")
            elif not isinstance(date_paiement, datetime):
                raise ValueError("La date de paiement doit être une chaîne ISO ou un objet datetime.")

        try:
            paiement_id = PaiementModel.create(facture_id, montant, methode.strip(), date_paiement)
            return paiement_id
        except Exception as e:
            raise Exception(f"Erreur lors de l'enregistrement du paiement : {e}")

    @staticmethod
    def get_paiements_par_facture(facture_id):
        if not facture_id:
            raise ValueError("L'ID de facture est obligatoire.")
        try:
            paiements = PaiementModel.get_by_facture(facture_id)
            return paiements
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des paiements : {e}")

    @staticmethod
    def supprimer_paiement(paiement_id):
        if not paiement_id:
            raise ValueError("L'ID de paiement est obligatoire.")
        try:
            success = PaiementModel.delete(paiement_id)
            if not success:
                raise Exception("La suppression du paiement a échoué.")
            return True
        except Exception as e:
            raise Exception(f"Erreur lors de la suppression du paiement : {e}")

    @staticmethod
    def mettre_a_jour_paiement(paiement_id, montant=None, methode=None, date_paiement=None):
        # Implémenter si besoin, sinon lever NotImplementedError
        raise NotImplementedError("Mise à jour des paiements non implémentée.")
