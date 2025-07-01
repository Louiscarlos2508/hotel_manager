from models.chambre_model import ChambreModel

# Il est préférable de définir les constantes à un seul endroit.
# Le modèle est un bon candidat, ou un fichier de constantes dédié.
# Supposons que le modèle expose cette constante.
VALID_STATUTS = ['libre', 'occupée', 'en nettoyage', 'hors service']


class ChambreController:
    """
    Contrôleur agissant comme intermédiaire entre la vue (UI) et le modèle (ChambreModel).
    Il valide les entrées et formate les réponses.
    """

    @staticmethod
    def create_chambre(numero: str, type_id: int, statut: str = 'libre'):
        """
        Valide les données et demande la création d'une nouvelle chambre au modèle.

        Returns:
            dict: Un dictionnaire indiquant le succès ou l'échec de l'opération.
        """
        try:
            if not numero or not isinstance(numero, str) or not numero.strip():
                return {"success": False, "error": "Le numéro de chambre est requis."}
            if not type_id or not isinstance(type_id, int):
                return {"success": False, "error": "Un type de chambre valide est requis."}
            if statut not in VALID_STATUTS:
                return {"success": False, "error": f"Statut invalide. Doit être l'un de : {VALID_STATUTS}"}

            last_id = ChambreModel.create(numero.strip(), type_id, statut)
            return {"success": True, "message": "Chambre créée avec succès.", "id": last_id}
        except Exception as e:
            # L'exception peut venir du modèle (ex: numéro de chambre déjà existant)
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_all_chambres():
        """Demande la liste de toutes les chambres au modèle."""
        try:
            chambres = ChambreModel.get_all()
            return {"success": True, "data": chambres}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_chambre_by_id(chambre_id: int):
        """Demande les détails d'une chambre spécifique."""
        try:
            # Utilise la méthode privée pour la validation et la récupération
            result = ChambreController._get_and_validate_chambre(chambre_id)
            if not result["success"]:
                return result

            return {"success": True, "data": result["chambre"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def update_chambre(chambre_id: int, numero: str, type_id: int, statut: str):
        """Valide et demande la mise à jour d'une chambre."""
        try:
            # 1. Valider l'existence de la chambre
            result = ChambreController._get_and_validate_chambre(chambre_id)
            if not result["success"]:
                return result

            # 2. Valider les nouvelles données
            if not numero or not isinstance(numero, str) or not numero.strip():
                return {"success": False, "error": "Le numéro de chambre est requis."}
            if not type_id or not isinstance(type_id, int):
                return {"success": False, "error": "Un type de chambre valide est requis."}
            if statut not in VALID_STATUTS:
                return {"success": False, "error": f"Statut invalide. Doit être l'un de : {VALID_STATUTS}"}

            # 3. Appeler le modèle
            if ChambreModel.update(chambre_id, numero.strip(), type_id, statut):
                return {"success": True, "message": "Chambre mise à jour avec succès."}
            else:
                return {"success": False, "error": "Aucune modification n'a été effectuée (données identiques ?)."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_chambre(chambre_id: int):
        """Demande la suppression d'une chambre après validation."""
        try:
            # Valider l'existence de la chambre avant de tenter de la supprimer
            result = ChambreController._get_and_validate_chambre(chambre_id)
            if not result["success"]:
                return result

            if ChambreModel.delete(chambre_id):
                return {"success": True, "message": "Chambre supprimée avec succès."}
            else:
                # Ce cas est peu probable si la validation a réussi, mais c'est une sécurité
                return {"success": False, "error": "La suppression a échoué."}
        except Exception as e:
            # Gère le cas où une chambre ne peut être supprimée (ex: clé étrangère dans réservations)
            return {"success": False,
                    "error": f"Impossible de supprimer la chambre. Elle est peut-être liée à des réservations. Détail : {e}"}

    # --- Méthodes privées et nouvelles fonctionnalités ---

    @staticmethod
    def _get_and_validate_chambre(chambre_id: int):
        """Méthode privée pour valider un ID et récupérer la chambre correspondante."""
        if not chambre_id or not isinstance(chambre_id, int):
            return {"success": False, "error": "L'ID de la chambre est invalide."}

        chambre = ChambreModel.get_by_id(chambre_id)
        if not chambre:
            return {"success": False, "error": f"Aucune chambre trouvée avec l'ID {chambre_id}."}

        return {"success": True, "chambre": chambre}

    @staticmethod
    def get_all_types_chambre():
        """Expose la fonctionnalité du modèle pour récupérer les types de chambre."""
        try:
            types = ChambreModel.get_all_types()
            return {"success": True, "data": types}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_chambres_disponibles(date_arrivee: str, date_depart: str):
        """Expose la fonctionnalité de recherche de chambres disponibles."""
        try:
            # Ajouter une validation de base pour les dates
            if not date_arrivee or not date_depart or date_arrivee >= date_depart:
                return {"success": False, "error": "Les dates d'arrivée et de départ sont invalides."}

            chambres = ChambreModel.get_chambres_disponibles(date_arrivee, date_depart)
            return {"success": True, "data": chambres}
        except Exception as e:
            return {"success": False, "error": str(e)}