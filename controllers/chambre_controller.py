from models.chambre_model import ChambreModel


class ChambreController:

    @staticmethod
    def create_chambre(numero, type_id, statut='libre'):
        try:
            if not numero or not isinstance(numero, str):
                return {"success": False,
                        "error": "Le numéro de chambre est requis et doit être une chaîne de caractères."}
            if not type_id or not isinstance(type_id, int):
                return {"success": False, "error": "Le type_id est requis et doit être un entier."}
            if statut not in ['libre', 'occupée', 'en maintenance']:
                statut = 'libre'  # valeur par défaut

            last_id = ChambreModel.create(numero, type_id, statut)
            return {"success": True, "message": "Chambre créée avec succès.", "id": last_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_all_chambres():
        try:
            chambres = ChambreModel.get_all()
            return {"success": True, "data": chambres}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_chambre_by_id(chambre_id):
        try:
            if not chambre_id or not isinstance(chambre_id, int):
                return {"success": False, "error": "ID chambre requis et doit être un entier."}
            chambre = ChambreModel.get_by_id(chambre_id)
            if chambre is None:
                return {"success": False, "error": "Chambre non trouvée."}
            return {"success": True, "data": chambre}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def update_chambre(chambre_id, numero=None, type_id=None, statut=None):
        try:
            if not isinstance(chambre_id, int) or chambre_id <= 0:
                return {"success": False, "error": "ID chambre requis et doit être un entier positif."}

            chambre = ChambreModel.get_by_id(chambre_id)
            if chambre is None:
                return {"success": False, "error": "Chambre non trouvée."}

            new_numero = numero if numero is not None else chambre['numero']
            new_type_id = type_id if type_id is not None else chambre['type_id']
            new_statut = statut if statut is not None else chambre['statut']

            if not isinstance(new_numero, str):
                return {"success": False, "error": "Le numéro doit être une chaîne de caractères."}
            if not isinstance(new_type_id, int) or new_type_id <= 0:
                return {"success": False, "error": "Le type_id doit être un entier positif."}
            if new_statut not in ['libre', 'occupée', 'en maintenance']:
                return {"success": False, "error": "Le statut doit être 'libre', 'occupée' ou 'en maintenance'."}

            fields = {
                "numero": new_numero,
                "type_id": new_type_id,
                "statut": new_statut
            }
            affected = ChambreModel.update(chambre_id, **fields)
            if affected == 0:
                return {"success": False, "error": "Aucune modification effectuée."}

            return {"success": True, "message": "Chambre mise à jour avec succès."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_chambre(chambre_id):
        try:
            if not chambre_id or not isinstance(chambre_id, int):
                return {"success": False, "error": "ID chambre requis et doit être un entier."}

            chambre = ChambreModel.get_by_id(chambre_id)
            if chambre is None:
                return {"success": False, "error": "Chambre non trouvée."}

            affected = ChambreModel.delete(chambre_id)
            if affected == 0:
                return {"success": False, "error": "Suppression non effectuée."}

            return {"success": True, "message": "Chambre supprimée avec succès."}
        except Exception as e:
            return {"success": False, "error": str(e)}
