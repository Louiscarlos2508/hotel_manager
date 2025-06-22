from models.user_model import UserModel

class UserController:

    @staticmethod
    def create_user(username, password, role, nom_complet=None):
        if not username or not password or not role:
            return {"success": False, "error": "Le nom d'utilisateur, le mot de passe et le rôle sont obligatoires."}

        existing_user = UserModel.get_by_username(username)
        if existing_user:
            return {"success": False, "error": "Ce nom d'utilisateur est déjà utilisé."}

        try:
            UserModel.create(username, password, role, nom_complet)
            return {"success": True, "message": "Utilisateur créé avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la création de l'utilisateur : {e}"}

    @staticmethod
    def get_all_users():
        try:
            users = UserModel.get_all()
            return {"success": True, "data": users}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération utilisateurs : {e}"}

    @staticmethod
    def get_user_by_username(username):
        if not username:
            return {"success": False, "error": "Le nom d'utilisateur est obligatoire."}
        try:
            user = UserModel.get_by_username(username)
            if not user:
                return {"success": False, "error": "Utilisateur non trouvé."}
            return {"success": True, "data": user}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération utilisateur : {e}"}

    @staticmethod
    def update_password(user_id, new_password):
        if not new_password:
            return {"success": False, "error": "Le nouveau mot de passe est obligatoire."}
        try:
            UserModel.update_password(user_id, new_password)
            return {"success": True, "message": "Mot de passe mis à jour."}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour mot de passe : {e}"}

    @staticmethod
    def set_active_status(user_id, actif):
        try:
            UserModel.set_active_status(user_id, actif)
            return {"success": True, "message": "Statut utilisateur mis à jour."}
        except Exception as e:
            return {"success": False, "error": f"Erreur changement statut utilisateur : {e}"}

    @staticmethod
    def update_user(user_id, nom_complet, role, actif):
        try:
            UserModel.update_user(user_id, nom_complet, role, actif)
            return {"success": True, "message": "Utilisateur mis à jour."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_user(user_id):
        try:
            UserModel.delete_user(user_id)
            return {"success": True, "message": "Utilisateur supprimé."}
        except Exception as e:
            return {"success": False, "error": str(e)}

