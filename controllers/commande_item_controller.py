from models.commande_item_model import CommandeItemModel


class CommandeItemController:

    @staticmethod
    def ajouter_item(commande_id, produit_id, quantite, prix_unitaire_capture):
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"success": False, "error": "ID commande invalide."}
        if not isinstance(produit_id, int) or produit_id <= 0:
            return {"success": False, "error": "ID produit invalide."}
        if not isinstance(quantite, int) or quantite <= 0:
            return {"success": False, "error": "La quantité doit être un entier positif."}
        if not (isinstance(prix_unitaire_capture, (int, float)) and prix_unitaire_capture >= 0):
            return {"success": False, "error": "Le prix unitaire doit être un nombre positif."}

        try:
            item_id = CommandeItemModel.add_item(commande_id, produit_id, quantite, prix_unitaire_capture)
            return {"success": True, "message": "Article ajouté à la commande.", "id": item_id}
        except Exception as e:
            return {"success": False, "error": f"Erreur ajout article commande : {e}"}

    @staticmethod
    def liste_items(commande_id):
        if not isinstance(commande_id, int) or commande_id <= 0:
            return {"success": False, "error": "ID commande invalide."}
        try:
            items = CommandeItemModel.get_items_by_commande(commande_id)
            return {"success": True, "data": items}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération articles commande : {e}"}

    @staticmethod
    def supprimer_item(item_id):
        if not isinstance(item_id, int) or item_id <= 0:
            return {"success": False, "error": "ID article invalide."}
        try:
            deleted = CommandeItemModel.delete(item_id)
            if deleted:
                return {"success": True, "message": "Article supprimé avec succès."}
            else:
                return {"success": False, "error": "Article non trouvé ou déjà supprimé."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression article commande : {e}"}

    @staticmethod
    def get_all():
        """Récupère TOUS les articles de TOUTES les commandes."""
        try:
            items = CommandeItemModel.get_all()
            # --- CORRECTION : Retourner un dictionnaire pour être cohérent ---
            return {"success": True, "data": items}
        except Exception as e:
            print(f"Erreur lors de la récupération de tous les articles de commande : {e}")
            return {"success": False, "error": str(e)}

    # --- NOUVELLE MÉTHODE POUR LE DASHBOARD ---
    @staticmethod
    def get_all_with_details():
        """Récupère TOUS les articles avec les détails de leur commande pour le dashboard."""
        try:
            items = CommandeItemModel.get_all_with_details()
            return {"success": True, "data": items}
        except Exception as e:
            print(f"Erreur lors de la récupération des détails des articles de commande : {e}")
            return {"success": False, "error": str(e)}


    @staticmethod
    def liste_items_details_par_lieu(lieu_consommation: str):
        """Récupère les détails de tous les articles pour un lieu donné."""
        try:
            items = CommandeItemModel.get_all_items_details_by_lieu(lieu_consommation)
            return {"success": True, "data": items}
        except Exception as e:
            return {"success": False, "error": str(e)}