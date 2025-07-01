from models.service_demande_model import ServiceDemandeModel

class ServiceDemandeController:

    @staticmethod
    def creer_demande(reservation_id, service_id, quantite, prix_capture, statut="Demandé"):
        if not reservation_id or not service_id or quantite <= 0 or prix_capture < 0:
            return {"success": False, "error": "Données de service invalides."}
        try:
            demande_id = ServiceDemandeModel.create(reservation_id, service_id, quantite, prix_capture, statut)
            return {"success": True, "demande_id": demande_id, "message": "Demande de service créée avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur création demande : {e}"}

    @staticmethod
    def lister_toutes_les_demandes():
        try:
            demandes = ServiceDemandeModel.get_all()
            return {"success": True, "data": demandes}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération demandes : {e}"}

    @staticmethod
    def lister_par_reservation(reservation_id):
        if not reservation_id or reservation_id <= 0:
            return {"success": False, "error": "ID réservation invalide."}
        try:
            services = ServiceDemandeModel.get_by_reservation(reservation_id)
            return {"success": True, "data": services}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération services pour réservation : {e}"}

    @staticmethod
    def changer_statut(demande_id, nouveau_statut):
        if not demande_id or not nouveau_statut:
            return {"success": False, "error": "ID ou statut manquant."}
        try:
            updated = ServiceDemandeModel.update_statut(demande_id, nouveau_statut)
            if not updated:
                return {"success": False, "error": "Mise à jour échouée ou demande introuvable."}
            return {"success": True, "message": "Statut mis à jour avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour statut : {e}"}

    @staticmethod
    def supprimer_demande(demande_id):
        if not demande_id or demande_id <= 0:
            return {"success": False, "error": "ID demande invalide."}
        try:
            deleted = ServiceDemandeModel.delete(demande_id)
            if not deleted:
                return {"success": False, "error": "Suppression échouée ou demande introuvable."}
            return {"success": True, "message": "Demande supprimée avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression demande : {e}"}
