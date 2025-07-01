from models.facture_item_model import FactureItemModel


class FactureItemController:

    @staticmethod
    def ajouter_item(facture_id, description, quantite, prix_unitaire,
                     date_prestation=None, commande_id=None, service_demande_id=None):
        if not facture_id or not isinstance(facture_id, int) or facture_id <= 0:
            return {"success": False, "error": "ID facture invalide."}
        if not description or not description.strip():
            return {"success": False, "error": "Description obligatoire."}
        if quantite is None or quantite <= 0:
            return {"success": False, "error": "Quantité invalide."}
        if prix_unitaire is None or prix_unitaire < 0:
            return {"success": False, "error": "Prix unitaire invalide."}

        try:
            item_id = FactureItemModel.create(
                facture_id,
                description.strip(),
                quantite,
                prix_unitaire,
                date_prestation,
                commande_id,
                service_demande_id
            )
            return {"success": True, "message": "Item ajouté à la facture.", "id": item_id}
        except Exception as e:
            return {"success": False, "error": f"Erreur ajout item : {e}"}

    @staticmethod
    def liste_items_par_facture(facture_id):
        if not facture_id or not isinstance(facture_id, int) or facture_id <= 0:
            return {"success": False, "error": "ID facture invalide."}
        try:
            items = FactureItemModel.get_by_facture(facture_id)
            return {"success": True, "data": items}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération items : {e}"}

    @staticmethod
    def modifier_item(item_id, quantite=None, prix_unitaire=None, description=None):
        if not item_id or not isinstance(item_id, int) or item_id <= 0:
            return {"success": False, "error": "ID item invalide."}
        if quantite is not None and quantite <= 0:
            return {"success": False, "error": "Quantité invalide."}
        if prix_unitaire is not None and prix_unitaire < 0:
            return {"success": False, "error": "Prix unitaire invalide."}
        if description is not None and not description.strip():
            return {"success": False, "error": "Description vide non autorisée."}

        try:
            success = FactureItemModel.update(item_id, quantite, prix_unitaire, description.strip() if description else None)
            if success:
                return {"success": True, "message": "Item mis à jour avec succès."}
            else:
                return {"success": False, "error": "Aucune modification effectuée ou item non trouvé."}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour item : {e}"}

    @staticmethod
    def supprimer_item(item_id):
        if not item_id or not isinstance(item_id, int) or item_id <= 0:
            return {"success": False, "error": "ID item invalide."}
        try:
            success = FactureItemModel.delete(item_id)
            if success:
                return {"success": True, "message": "Item supprimé avec succès."}
            else:
                return {"success": False, "error": "Item non trouvé ou déjà supprimé."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression item : {e}"}
