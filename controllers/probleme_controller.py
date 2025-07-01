from models.probleme_model import ProblemeModel


class ProblemeController:

    @staticmethod
    def signaler_probleme(chambre_id, description, signale_par_user_id=None, priorite="Moyenne"):
        if not chambre_id or not isinstance(chambre_id, int):
            return {"success": False, "error": "ID de chambre invalide."}
        if not description or description.strip() == "":
            return {"success": False, "error": "La description du problème est obligatoire."}
        try:
            # Le statut par défaut 'Nouveau' est géré par la base de données, c'est parfait.
            probleme_id = ProblemeModel.create(chambre_id, description.strip(), signale_par_user_id, priorite)
            return {"success": True, "probleme_id": probleme_id, "message": "Problème signalé avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur signalement problème : {e}"}

    @staticmethod
    def liste_problemes():
        """
        Récupère la liste des problèmes avec les détails de la chambre.
        Le modèle 'ProblemeModel.get_all()' fait déjà le travail de jointure.
        """
        try:
            problemes = ProblemeModel.get_all()
            return {"success": True, "data": problemes}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération des problèmes : {e}"}

    @staticmethod
    def get_probleme(probleme_id):
        if not probleme_id or not isinstance(probleme_id, int):
            return {"success": False, "error": "ID du problème invalide."}
        try:
            probleme = ProblemeModel.get_by_id(probleme_id)
            if not probleme:
                return {"success": False, "error": "Problème non trouvé."}
            return {"success": True, "data": probleme}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération problème : {e}"}

    @staticmethod
    def mettre_a_jour_statut(probleme_id, nouveau_statut):
        """Met à jour le statut d'un problème."""
        if not probleme_id or not isinstance(probleme_id, int):
            return {"success": False, "error": "ID du problème invalide."}

        # --- CORRECTION ---
        # On utilise les statuts définis dans le schéma de la base de données.
        statuts_valides = ["Nouveau", "En cours", "Résolu", "Annulé"]
        if nouveau_statut not in statuts_valides:
            return {"success": False, "error": f"Statut non valide. Doit être l'un de : {', '.join(statuts_valides)}"}

        try:
            # La logique de la date de résolution est déjà dans le modèle, on peut simplifier ici.
            success = ProblemeModel.update_statut(probleme_id, nouveau_statut)
            if not success:
                return {"success": False, "error": "Mise à jour échouée ou problème introuvable."}
            return {"success": True, "message": "Statut du problème mis à jour avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour statut : {e}"}

    @staticmethod
    def supprimer_probleme(probleme_id):
        if not probleme_id or not isinstance(probleme_id, int):
            return {"success": False, "error": "ID du problème invalide."}
        try:
            success = ProblemeModel.delete(probleme_id)
            if not success:
                return {"success": False, "error": "Suppression échouée ou problème introuvable."}
            return {"success": True, "message": "Problème supprimé avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression problème : {e}"}