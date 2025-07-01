from werkzeug.security import check_password_hash
from database.db import get_connection


# La fonction hash_password() est incorrecte pour ce cas d'usage et doit être supprimée.

def login_user(username, password):
    """
    Vérifie les identifiants d'un utilisateur et retourne ses informations s'il est valide.

    Args:
        username (str): Le nom d'utilisateur.
        password (str): Le mot de passe en clair.

    Returns:
        dict: Un dictionnaire contenant les informations de l'utilisateur si la connexion réussit.
        None: Si le nom d'utilisateur n'existe pas ou si le mot de passe est incorrect.
    """
    # Le 'with' garantit que la connexion à la base de données sera fermée
    # automatiquement, même en cas d'erreur.
    with get_connection() as conn:
        cursor = conn.cursor()

        # Étape 1: Récupérer l'utilisateur par son nom d'utilisateur.
        # On récupère aussi le hash du mot de passe pour le vérifier.
        cursor.execute(
            "SELECT id, username, password_hash, role, nom_complet FROM users WHERE username=? AND actif=1",
            (username,)
        )
        user_data = cursor.fetchone()

        # Étape 2: Vérifier si l'utilisateur existe ET si le mot de passe est correct.
        # check_password_hash s'occupe de tout pour nous.
        if user_data and check_password_hash(user_data['password_hash'], password):
            # Le mot de passe est correct, on retourne les informations.
            # On accède aux colonnes par leur nom, c'est plus clair et plus sûr.
            return {
                "id": user_data['id'],
                "username": user_data['username'],
                "role": user_data['role'],
                "nom_complet": user_data['nom_complet']
            }

    # Si l'utilisateur n'existe pas, si le mot de passe est incorrect,
    # ou si une erreur est survenue, on retourne None.
    return None