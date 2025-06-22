from models.consommation_model import ConsommationModel

class ConsommationController:

    @staticmethod
    def add_consommation(reservation_id, designation, quantite=1, prix_unitaire=0.0):
        if not isinstance(reservation_id, int) or reservation_id <= 0:
            return {"success": False, "error": "Reservation ID invalide."}
        if not designation or not isinstance(designation, str):
            return {"success": False, "error": "Désignation obligatoire."}
        if quantite < 1:
            return {"success": False, "error": "La quantité doit être au moins 1."}
        if prix_unitaire < 0:
            return {"success": False, "error": "Le prix unitaire ne peut pas être négatif."}

        try:
            result = ConsommationModel.create(reservation_id, designation.strip(), quantite, prix_unitaire)
            if result is None:
                return {"success": False, "error": "Erreur lors de la création de la consommation."}
            return {"success": True, "id": result}
        except Exception as e:
            return {"success": False, "error": f"Erreur création consommation : {e}"}

    @staticmethod
    def get_consommations_by_reservation(reservation_id):
        if not isinstance(reservation_id, int) or reservation_id <= 0:
            return {"success": False, "error": "Reservation ID invalide."}
        try:
            consommations = ConsommationModel.get_by_reservation(reservation_id)
            return {"success": True, "data": consommations}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération consommations : {e}"}

    @staticmethod
    def update_consommation(consommation_id, reservation_id=None, designation=None, quantite=None, prix_unitaire=None):
        if not isinstance(consommation_id, int) or consommation_id <= 0:
            return {"success": False, "error": "ID de consommation invalide."}
        if not isinstance(reservation_id, int) or reservation_id <= 0:
            return {"success": False, "error": "ID de réservation invalide."}
        if quantite is not None and quantite < 1:
            return {"success": False, "error": "La quantité doit être au moins 1."}
        if prix_unitaire is not None and prix_unitaire < 0:
            return {"success": False, "error": "Le prix unitaire ne peut pas être négatif."}
        if designation is not None and (not isinstance(designation, str) or designation.strip() == ""):
            return {"success": False, "error": "La désignation doit être une chaîne non vide."}

        try:
            success = ConsommationModel.update(
                consommation_id,
                reservation_id,
                designation,
                quantite,
                prix_unitaire
            )
            if not success:
                return {"success": False, "error": "Aucune modification effectuée."}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour consommation : {e}"}

    @staticmethod
    def delete_consommation(consommation_id):
        if not isinstance(consommation_id, int) or consommation_id <= 0:
            return {"success": False, "error": "ID de consommation invalide."}
        try:
            success = ConsommationModel.delete(consommation_id)
            if not success:
                return {"success": False, "error": "Erreur lors de la suppression de la consommation."}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression consommation : {e}"}

    @staticmethod
    def get_consommations_by_date_range(start_date, end_date):
        # Ici on suppose start_date et end_date sont des string 'YYYY-MM-DD' ou objets date
        try:
            consommations = ConsommationModel.get_between_dates(start_date, end_date)
            return {"success": True, "data": consommations}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération consommations par date : {e}"}

    @staticmethod
    def get_all_consommations():
        try:
            consommations = ConsommationModel.get_all()
            return {"success": True, "data": consommations}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération de toutes les consommations : {e}"}
