# /home/soutonnoma/PycharmProjects/HotelManager/controllers/log_controller.py
from models.log_model import LogModel

class LogController:
    """
    Contrôleur pour la gestion des logs.
    Il est conçu pour être instancié avec l'ID de l'utilisateur courant.
    """

    def __init__(self, user_id=None):
        """
        Initialise le contrôleur avec l'ID de l'utilisateur effectuant les actions.
        """
        self.user_id = user_id

    def log_action(self, action: str, details: str = ""):
        """
        Enregistre une action de l'utilisateur.
        Gère les cas où l'user_id n'est pas défini pour ne pas causer d'erreur.
        """
        # Si le contrôleur a été initialisé sans user_id, on ne fait rien.
        # C'est une sécurité pour les actions système ou les cas non prévus.
        if self.user_id is None:
            print(f"Warning: Log action '{action}' attempted without a valid user_id.")
            return

        try:
            # Délègue la création au modèle.
            LogModel.create(self.user_id, action, details)
        except Exception as e:
            # La journalisation ne doit jamais interrompre le flux principal de l'application.
            # L'erreur est déjà affichée dans la console par le modèle.
            pass

    @staticmethod
    def get_logs(limit=100):
        """
        Récupère les logs via le modèle.
        Retourne une réponse standardisée pour l'interface utilisateur.
        """
        try:
            logs = LogModel.get_all(limit)
            return {"success": True, "data": logs}
        except Exception as e:
            # Ce cas est peu probable, car le modèle gère déjà les erreurs,
            # mais c'est une bonne pratique.
            return {"success": False, "error": f"Erreur lors de la récupération des logs : {e}"}