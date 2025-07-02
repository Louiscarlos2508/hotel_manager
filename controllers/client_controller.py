# /home/soutonnoma/PycharmProjects/HotelManager/controllers/client_controller.py

from models.client_model import ClientModel


class ClientController:

    @staticmethod
    def ajouter_client(nom, prenom=None, tel=None, email=None, cni=None, adresse=None):
        if not nom or not nom.strip():
            return {"success": False, "error": "Le nom du client est obligatoire."}
        if not tel or not tel.strip():
            return {"success": False, "error": "Le numéro de téléphone est obligatoire."}
        if not email or not email.strip():
            return {"success": False, "error": "L'adresse email est obligatoire."}
        if not cni or not cni.strip():
            return {"success": False, "error": "Le numéro de CNI est obligatoire."}
        try:
            client_id = ClientModel.create(nom, prenom, tel, email, cni, adresse)
            return {"success": True, "message": "Client ajouté avec succès.", "id": client_id}
        except Exception as e:
            return {"success": False, "error": f"Erreur création client: {e}"}

    @staticmethod
    def liste_clients():
        try:
            clients = ClientModel.get_all()
            return {"success": True, "data": clients}
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
            return {"success": True, "data": client}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération client: {e}"}

    @staticmethod
    def modifier_client(client_id, nom=None, prenom=None, tel=None, email=None, cni=None, adresse=None):
        """
        Méthode corrigée pour utiliser correctement la méthode `update` du modèle.
        """
        if not isinstance(client_id, int) or client_id <= 0:
            return {"success": False, "error": "ID client invalide."}
        if nom is not None and not nom.strip():
            return {"success": False, "error": "Le nom ne peut pas être vide."}

        try:
            # On vérifie d'abord que le client existe
            exists = ClientModel.get_by_id(client_id)
            if exists is None:
                return {"success": False, "error": "Client non trouvé."}

            # --- CORRECTION ---
            # On construit un dictionnaire avec les arguments fournis
            # pour utiliser la puissance de la méthode `update` du modèle.
            update_data = {
                "nom": nom,
                "prenom": prenom,
                "tel": tel,
                "email": email,
                "cni": cni,
                "adresse": adresse
            }

            # On passe ce dictionnaire en tant que kwargs.
            # Le modèle se chargera de ne mettre à jour que les champs non-None.
            updated = ClientModel.update(client_id, **update_data)

            if not updated:
                # Cela peut arriver si les données fournies sont identiques aux données existantes.
                return {"success": True, "message": "Aucune modification nécessaire (données identiques)."}

            return {"success": True, "message": "Client mis à jour avec succès."}
        except Exception as e:
            # Le modèle lèvera une exception en cas de conflit (ex : email déjà pris)
            return {"success": False, "error": f"Erreur mise à jour client: {e}"}

    @staticmethod
    def supprimer_client(client_id):
        if not isinstance(client_id, int) or client_id <= 0:
            return {"success": False, "error": "ID client invalide."}
        try:
            # La logique de suppression est déjà bonne, car elle appelle une méthode dédiée du modèle.
            # On la garde telle quelle.
            ClientModel.delete(client_id)
            return {"success": True, "message": "Client supprimé avec succès."}
        except Exception as e:
            # Le modèle lèvera une exception si le client a des réservations.
            return {"success": False, "error": f"Erreur suppression client: {e}"}

    @staticmethod
    def liste_clients_avec_reservations():
        try:
            clients = ClientModel.get_all_with_reservation_count()
            return {"success": True, "data": clients}
        except Exception as e:
            return {"success": False, "error": str(e)}