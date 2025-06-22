from models.hotel_info_model import HotelInfoModel

class HotelInfoController:

    @staticmethod
    def get_info():
        try:
            info = HotelInfoModel.get_info()
            if info is None:
                return {"success": False, "error": "Aucune information trouvée."}
            return {"success": True, "data": info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def save_info(nom, adresse, telephone, email, siret):
        if not nom or nom.strip() == "":
            return {"success": False, "error": "Le nom de l'hôtel est obligatoire."}
        try:
            HotelInfoModel.save_info(nom.strip(), adresse, telephone, email, siret)
            return {"success": True, "message": "Informations enregistrées avec succès."}
        except Exception as e:
            return {"success": False, "error": str(e)}
