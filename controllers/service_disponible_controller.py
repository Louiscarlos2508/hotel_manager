from models.service_disponible_model import ServiceDisponibleModel

class ServiceDisponibleController:

    @staticmethod
    def ajouter_service(nom_service, description=None, prix=0.0):
        if not nom_service or prix < 0:
            return {"success": False, "error": "Données du service invalides."}
        try:
            service_id = ServiceDisponibleModel.create(nom_service, description, prix)
            return {"success": True, "service_id": service_id, "message": "Service ajouté avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur création service : {e}"}

    @staticmethod
    def lister_services():
        try:
            services = ServiceDisponibleModel.get_all()
            return {"success": True, "data": services}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération services : {e}"}

    @staticmethod
    def modifier_service(service_id, **kwargs):
        if not service_id or service_id <= 0:
            return {"success": False, "error": "ID service invalide."}
        try:
            updated = ServiceDisponibleModel.update(service_id, **kwargs)
            if not updated:
                return {"success": False, "error": "Mise à jour échouée ou aucune donnée modifiée."}
            return {"success": True, "message": "Service mis à jour avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour : {e}"}

    @staticmethod
    def supprimer_service(service_id):
        if not service_id or service_id <= 0:
            return {"success": False, "error": "ID service invalide."}
        try:
            deleted = ServiceDisponibleModel.delete(service_id)
            if not deleted:
                return {"success": False, "error": "Suppression échouée ou service introuvable."}
            return {"success": True, "message": "Service supprimé avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression : {e}"}
