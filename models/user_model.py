import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from werkzeug.security import generate_password_hash, check_password_hash

from models.base_model import BaseModel


class UserModel(BaseModel):
    """
    Modèle pour gérer les utilisateurs (users) dans la base de données.
    Utilise un hashage de mot de passe robuste avec Werkzeug.
    """

    @classmethod
    def get_by_username(cls, username: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son nom d'utilisateur."""
        query = "SELECT * FROM users WHERE username = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (username,))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur de récupération de l'utilisateur {username}: {e}") from e

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        """Récupère tous les utilisateurs avec des informations non sensibles."""
        query = "SELECT id, username, nom_complet, role, actif FROM users WHERE is_deleted = 0 ORDER BY nom_complet"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                # La conversion en dict(row) est plus propre et robuste
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur de récupération de tous les utilisateurs : {e}") from e

    @classmethod
    def create(cls, username: str, password: str, role: str, nom_complet: Optional[str] = None, actif: bool = True) -> int:
        """
        Crée un nouvel utilisateur avec un mot de passe hashé par Werkzeug.
        """
        # Utilisation de generate_password_hash pour un hashage sécurisé (avec sel)
        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO users (username, password_hash, role, nom_complet, actif)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (username, password_hash, role, nom_complet, int(actif)))
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError as e:
            # Cette erreur se produit si l'username est déjà pris (contrainte UNIQUE)
            raise Exception(f"Le nom d'utilisateur '{username}' est déjà utilisé.") from e
        except sqlite3.Error as e:
            raise Exception(f"Erreur base de données lors de la création de l'utilisateur : {e}") from e

    @classmethod
    def update_password(cls, user_id: int, new_password: str) -> bool:
        """Met à jour le mot de passe d'un utilisateur."""
        password_hash = generate_password_hash(new_password)
        query = "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ? AND is_deleted = 0"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (password_hash, timestamp_actuel, user_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur de mise à jour du mot de passe pour l'utilisateur {user_id}: {e}") from e

    @classmethod
    def check_password(cls, username: str, password: str) -> bool:
        """
        Vérifie si le mot de passe fourni correspond à celui de l'utilisateur.
        C'est la méthode à utiliser pour la connexion (login).
        """
        user = cls.get_by_username(username)
        if user and 'password_hash' in user:
            return check_password_hash(user['password_hash'], password)
        return False

    @classmethod
    def set_active_status(cls, user_id: int, actif: bool) -> bool:
        """Active ou désactive un utilisateur."""
        query = "UPDATE users SET actif = ?, updated_at = ? WHERE id = ? AND is_deleted = 0"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (int(actif), timestamp_actuel, user_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur de changement de statut pour l'utilisateur {user_id}: {e}") from e

    @classmethod
    def update_user(cls, user_id: int, nom_complet: str, role: str, actif: bool) -> bool:
        """Met à jour les informations d'un utilisateur (sans le mot de passe)."""
        query = "UPDATE users SET nom_complet = ?, role = ?, actif = ?, updated_at = ? WHERE id = ? AND is_deleted = 0"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (nom_complet, role, int(actif), timestamp_actuel, user_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur de mise à jour de l'utilisateur {user_id}: {e}") from e

    @classmethod
    def delete_user(cls, user_id: int) -> bool:

        """
        Effectue une suppression logique (soft delete) d'un utilisateur.
        Ajoute une protection pour ne pas supprimer l'utilisateur 'admin'.
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()

                # --- AMÉLIORATION : Protection de l'admin ---
                cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
                user = cur.fetchone()
                if user and user['username'] == 'admin':
                    raise Exception("La suppression de l'utilisateur 'admin' principal n'est pas autorisée.")
                # --- FIN DE L'AMÉLIORATION ---

                query = "UPDATE users SET is_deleted = 1, updated_at = ? WHERE id = ?"
                timestamp_actuel = datetime.now(timezone.utc).isoformat()
                cur.execute(query, (timestamp_actuel, user_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur de suppression de l'utilisateur {user_id}: {e}") from e