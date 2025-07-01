from models.types_chambre_model import TypesChambreModel

class TypesChambreController:

    @staticmethod
    def ajouter_type(nom, description, prix_par_nuit):
        if not nom or prix_par_nuit is None or prix_par_nuit < 0:
            return {"success": False, "error": "Données invalides pour le type de chambre."}
        try:
            type_id = TypesChambreModel.create(nom, description, prix_par_nuit)
            return {"success": True, "type_id": type_id, "message": "Type de chambre ajouté avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur ajout type chambre : {e}"}

    @staticmethod
    def lister_types():
        try:
            types = TypesChambreModel.get_all()
            return {"success": True, "data": types}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération des types : {e}"}

    @staticmethod
    def get_par_id(type_id):
        if not type_id or type_id <= 0:
            return {"success": False, "error": "ID type invalide."}
        try:
            type_data = TypesChambreModel.get_by_id(type_id)
            if not type_data:
                return {"success": False, "error": "Type de chambre introuvable."}
            return {"success": True, "data": type_data}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération type chambre : {e}"}

    @staticmethod
    def modifier_type(type_id, nom, description, prix_par_nuit):
        if not type_id or type_id <= 0:
            return {"success": False, "error": "ID type invalide."}
        if not nom or prix_par_nuit is None or prix_par_nuit < 0:
            return {"success": False, "error": "Données de modification invalides."}
        try:
            updated = TypesChambreModel.update(type_id, nom, description, prix_par_nuit)
            if not updated:
                return {"success": False, "error": "Aucune modification effectuée."}
            return {"success": True, "message": "Type de chambre modifié avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur modification type chambre : {e}"}

    @staticmethod
    def supprimer_type(type_id):
        if not type_id or type_id <= 0:
            return {"success": False, "error": "ID type invalide."}
        try:
            deleted = TypesChambreModel.delete(type_id)
            if not deleted:
                return {"success": False, "error": "Suppression échouée ou type introuvable."}
            return {"success": True, "message": "Type de chambre supprimé avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression type chambre : {e}"}
