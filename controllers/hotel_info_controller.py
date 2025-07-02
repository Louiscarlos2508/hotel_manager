# /home/soutonnoma/PycharmProjects/HotelManager/controllers/hotel_info_controller.py

from models.hotel_info_model import HotelInfoModel


class HotelInfoController:
    @staticmethod
    def get_info():
        try:
            info = HotelInfoModel.get_info()
            return {"success": True, "data": info}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération des informations : {e}"}

    @staticmethod
    def save_info(nom, adresse, telephone, email, siret, tva_hebergement, tva_restauration, tdt_par_personne):
        """Valide et demande la sauvegarde des informations de l'hôtel."""
        if not nom:
            return {"success": False, "error": "Le nom de l'hôtel est obligatoire."}
        if not (0 <= tva_hebergement <= 1) or not (0 <= tva_restauration <= 1):
            return {"success": False, "error": "Les taux de TVA doivent être des décimaux entre 0 et 1."}
        if tdt_par_personne < 0:
            return {"success": False, "error": "La TDT ne peut pas être négative."}

        try:
            HotelInfoModel.save_info(nom, adresse, telephone, email, siret, tva_hebergement, tva_restauration,
                                     tdt_par_personne)
            return {"success": True, "message": "Informations de l'hôtel enregistrées."}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la sauvegarde : {e}"}