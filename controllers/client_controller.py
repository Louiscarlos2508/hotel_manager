from models.client_model import ClientModel

class ClientController:

    @staticmethod
    def ajouter_client(nom, prenom=None, tel=None, email=None, cni=None, adresse=None):
        if not nom or nom.strip() == "":
            return {"success": False, "error": "Le nom est obligatoire."}
        try:
            result = ClientModel.create(nom.strip(), prenom, tel, email, cni, adresse)
            return {"success": True, "message": "Client ajouté avec succès.", "id": result}
        except Exception as e:
            return {"success": False, "error": f"Erreur création client: {e}"}

    @staticmethod
    def liste_clients():
        try:
            clients = ClientModel.get_all()
            return {"success": True, "clients": clients}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération clients: {e}"}

    @staticmethod
    def obtenir_client(client_id):
        if not isinstance(client_id, int) or client_id <= 0:
            return {"success": False, "error": "ID client invalide."}
        try:
            client = ClientModel.get_by_id(client_id)
            if client is None:
                return {"success": False, "error": "Client non trouvé."}
            return {"success": True, "client": client}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération client: {e}"}

    @staticmethod
    def modifier_client(client_id, nom=None, prenom=None, tel=None, email=None, cni=None, adresse=None):
        if not isinstance(client_id, int) or client_id <= 0:
            return {"success": False, "error": "ID client invalide."}
        if nom is not None and nom.strip() == "":
            return {"success": False, "error": "Le nom ne peut pas être vide."}
        try:
            exists = ClientModel.get_by_id(client_id)
            if exists is None:
                return {"success": False, "error": "Client non trouvé."}

            updated = ClientModel.update(client_id, nom, prenom, tel, email, cni, adresse)
            if updated == 0:
                return {"success": False, "error": "Aucune modification effectuée."}
            return {"success": True, "message": "Client mis à jour avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour client: {e}"}

    @staticmethod
    def supprimer_client(client_id):
        if not isinstance(client_id, int) or client_id <= 0:
            return {"success": False, "error": "ID client invalide."}
        try:
            exists = ClientModel.get_by_id(client_id)
            if not exists:
                return {"success": False, "error": "Client non trouvé."}

            deleted = ClientModel.delete(client_id)
            if deleted == 0:
                return {"success": False, "error": "Impossible de supprimer un client lié à une réservation."}
            return {"success": True, "message": "Client supprimé avec succès."}
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression client: {e}"}

    @staticmethod
    def liste_clients_avec_reservations():
        try:
            clients = ClientModel.get_all_with_reservation_count()
            return {"success": True, "clients": clients}
        except Exception as e:
            return {"success": False, "error": str(e)}

