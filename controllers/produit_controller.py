from models.produit_model import ProduitModel

class ProduitController:

    @staticmethod
    def ajouter_produit(nom, description, categorie, prix_unitaire, disponible=True):
        if not nom or not categorie or prix_unitaire is None:
            return {"success": False, "error": "Les champs nom, catégorie et prix unitaire sont obligatoires."}
        try:
            produit_id = ProduitModel.create(nom.strip(), description, categorie.strip(), prix_unitaire, disponible)
            return {"success": True, "message": "Produit ajouté avec succès.", "id": produit_id}
        except Exception as e:
            return {"success": False, "error": f"Erreur ajout produit : {e}"}

    @staticmethod
    def liste_produits():
        try:
            produits = ProduitModel.get_all()
            return {"success": True, "data": produits}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération produits : {e}"}

    @staticmethod
    def obtenir_produit(produit_id):
        try:
            produit = ProduitModel.get_by_id(produit_id)
            if produit:
                return {"success": True, "data": produit}
            else:
                return {"success": False, "error": "Produit non trouvé."}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération produit : {e}"}

    @staticmethod
    def modifier_produit(produit_id, nom=None, description=None, categorie=None, prix_unitaire=None, disponible=None):
        if not produit_id or not isinstance(produit_id, int):
            return {"success": False, "error": "ID produit invalide."}
        try:
            success = ProduitModel.update(produit_id, nom, description, categorie, prix_unitaire, disponible)
            if success:
                return {"success": True, "message": "Produit mis à jour avec succès."}
            else:
                return {"success": False, "error": "Aucune mise à jour effectuée."}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour produit : {e}"}

    @staticmethod
    def supprimer_produit(produit_id):
        if not produit_id or not isinstance(produit_id, int):
            return {"success": False, "error": "ID produit invalide."}
        try:
            success = ProduitModel.delete(produit_id)
            if success:
                return {"success": True, "message": "Produit supprimé avec succès."}
            else:
                return {"success": False, "error": "Produit non trouvé ou déjà supprimé."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression produit : {e}"}
