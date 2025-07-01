from models.commande_model import CommandeModel


class CommandeController:

    @staticmethod
    def creer_commande(reservation_id, user_id_saisie=None, lieu_consommation='Room Service'):
        if not isinstance(reservation_id, int) or reservation_id <= 0:
            return {"success": False, "error": "ID réservation invalide."}
        if lieu_consommation not in ['Room Service', 'Restaurant', 'Bar']:  # adapter selon tes lieux valides
            return {"success": False, "error": "Lieu de consommation invalide."}
        try:
            commande_id = CommandeModel.create(reservation_id, user_id_saisie, lieu_consommation)
            return {"success": True, "message": "Commande créée avec succès.", "id": commande_id}
        except Exception as e:
            return {"success": False, "error": f"Erreur création commande : {e}"}

    @staticmethod
    def liste_commandes():
        try:
            commandes = CommandeModel.get_all()
            return {"success": True, "data": commandes}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération commandes : {e}"}


    @staticmethod
    def modifier_statut(commande_id, nouveau_statut):
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"success": False, "error": "ID commande invalide."}
        if nouveau_statut not in ['En cuisine', 'En livraison', 'Livré', 'Annulé']:  # adapter selon les statuts valides
            return {"success": False, "error": "Statut invalide."}
        try:
            success = CommandeModel.update_statut(commande_id, nouveau_statut)
            if success:
                return {"success": True, "message": "Statut modifié avec succès."}
            else:
                return {"success": False, "error": "Commande non trouvée ou statut non modifié."}
        except Exception as e:
            return {"success": False, "error": f"Erreur modification statut commande : {e}"}

    @staticmethod
    def supprimer_commande(commande_id):
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"success": False, "error": "ID commande invalide."}
        try:
            success = CommandeModel.delete(commande_id)
            if success:
                return {"success": True, "message": "Commande supprimée avec succès."}
            else:
                return {"success": False, "error": "Commande non trouvée ou déjà supprimée."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression commande : {e}"}



    @staticmethod
    def get_or_create_commande(reservation_id, user_id_saisie=None, lieu_consommation='Room Service'):
        """
        Cherche une commande existante pour la réservation et le lieu.
        Si elle n'existe pas, la crée. Retourne l'ID de la commande.
        """
        if not isinstance(reservation_id, int) or reservation_id <= 0:
            return {"success": False, "error": "ID réservation invalide."}
        try:
            # 1. Chercher une commande existante
            existing_commande = CommandeModel.find_by_reservation_and_lieu(reservation_id, lieu_consommation)
            if existing_commande:
                return {"success": True, "id": existing_commande['id'], "message": "Commande existante trouvée."}

            # 2. Si non trouvée, en créer une nouvelle
            commande_id = CommandeModel.create(reservation_id, user_id_saisie, lieu_consommation)
            return {"success": True, "id": commande_id, "message": "Nouvelle commande créée."}

        except Exception as e:
            return {"success": False, "error": f"Erreur gestion commande : {e}"}



    @staticmethod
    def liste_commandes_par_reservation(reservation_id):
        """Retrieves all orders for a specific reservation."""
        if not isinstance(reservation_id, int) or reservation_id <= 0:
            return {"success": False, "error": "Invalid reservation ID."}
        try:
            commandes = CommandeModel.get_by_reservation(reservation_id)
            return {"success": True, "data": commandes}
        except Exception as e:
            return {"success": False, "error": f"Error retrieving orders: {e}"}