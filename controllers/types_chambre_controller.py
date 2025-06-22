from models.types_chambre_model import TypesChambreModel

class TypesChambreController:

    @staticmethod
    def create_type_chambre(nom, description=None, prix_par_nuit=0):
        if not nom or not isinstance(nom, str):
            return {"success": False, "error": "Le nom est obligatoire."}
        if not isinstance(prix_par_nuit, (int, float)) or prix_par_nuit < 0:
            return {"success": False, "error": "Le prix par nuit doit être un nombre positif."}

        try:
            type_id = TypesChambreModel.create(nom, description, prix_par_nuit)
            return {"success": True, "message": "Type de chambre ajouté.", "id": type_id}
        except Exception as e:
            return {"success": False, "error": f"Erreur création type chambre : {e}"}

    @staticmethod
    def get_all_types_chambre():
        try:
            data = TypesChambreModel.get_all()
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération types chambre : {e}"}

    @staticmethod
    def get_type_chambre_by_id(type_id):
        if not type_id:
            return {"success": False, "error": "ID requis."}
        try:
            type_data = TypesChambreModel.get_by_id(type_id)
            if not type_data:
                return {"success": False, "error": "Type de chambre non trouvé."}
            return {"success": True, "data": type_data}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération type chambre : {e}"}

    @staticmethod
    def update_type_chambre(type_id, nom, description=None, prix_par_nuit=0):
        if not type_id:
            return {"success": False, "error": "ID requis."}
        if not nom:
            return {"success": False, "error": "Nom requis."}
        if not isinstance(prix_par_nuit, (int, float)) or prix_par_nuit < 0:
            return {"success": False, "error": "Prix invalide."}

        try:
            count = TypesChambreModel.update(type_id, nom, description, prix_par_nuit)
            if count == 0:
                return {"success": False, "error": "Aucune modification effectuée."}
            return {"success": True, "message": "Type de chambre mis à jour."}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour type chambre : {e}"}

    @staticmethod
    def delete_type_chambre(type_id):
        if not type_id:
            return {"success": False, "error": "ID requis."}
        try:
            count = TypesChambreModel.delete(type_id)
            if count == 0:
                return {"success": False, "error": "Suppression non effectuée."}
            return {"success": True, "message": "Type de chambre supprimé."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression type chambre : {e}"}
