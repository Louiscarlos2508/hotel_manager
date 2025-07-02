# /home/soutonnoma/PycharmProjects/HotelManager/database/db.py
import sqlite3
import os
from werkzeug.security import generate_password_hash

# Le chemin absolu est une excellente pratique, on le conserve.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "hotel.db")


def get_connection():
    """
    Établit et retourne une connexion à la base de données.
    Cette connexion est configurée pour :
    1. Forcer les contraintes de clé étrangère (CRUCIAL pour l'intégrité des données).
    2. Retourner les résultats sous forme de lignes de type dictionnaire.
    """
    conn = sqlite3.connect(DB_PATH)

    # --- AMÉLIORATION CRUCIALE ---
    # Force SQLite à respecter les règles de clé étrangère définies dans votre schéma.
    # Cela empêche, par exemple, de supprimer une chambre si elle a des réservations.
    conn.execute("PRAGMA foreign_keys = ON;")

    # Permet d'accéder aux colonnes par leur nom (ex: row['numero'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialise la base de données. Crée le schéma et les utilisateurs
    par défaut si la base de données n'existe pas.
    """
    if not os.path.exists(DB_PATH):
        print("ℹ️ Base de données non trouvée. Création en cours...")
        conn = None
        try:
            # get_connection() va maintenant créer une connexion sécurisée
            conn = get_connection()

            schema_path = os.path.join(PROJECT_ROOT, "database", "schema_hotel.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            print("✅ Schéma de la base de données créé.")

            create_default_users(conn)

            conn.commit()
            print("✅ Base de données initialisée avec succès.")

        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'initialisation de la base de données : {e}")
        finally:
            if conn:
                conn.close()
    else:
        print("ℹ️ Base de données déjà existante.")


def create_default_users(conn):
    """Crée un ensemble d'utilisateurs par défaut dans la base de données."""
    cursor = conn.cursor()
    users_to_create = [
        ('admin', 'admin123', 'admin', 'Administrateur Système', 1),
        ('reception', 'reception123', 'reception', 'Agent de Réception', 1),
        ('manager', 'manager123', 'manager', 'Manager Restauration', 1)
    ]
    users_data_for_db = [
        (user, generate_password_hash(pw), role, name, act)
        for user, pw, role, name, act in users_to_create
    ]
    cursor.executemany(
        "INSERT INTO users (username, password_hash, role, nom_complet, actif) VALUES (?, ?, ?, ?, ?)",
        users_data_for_db
    )
    print(f"✅ {len(users_to_create)} utilisateurs par défaut créés.")


if __name__ == '__main__':
    print("Initialisation manuelle de la base de données...")
    if os.path.exists(DB_PATH):
        response = input(f"Le fichier '{DB_PATH}' existe déjà. Voulez-vous le supprimer et le recréer ? (oui/non): ")
        if response.lower() == 'oui':
            os.remove(DB_PATH)
            print(f"Fichier '{DB_PATH}' supprimé.")
            init_db()
        else:
            print("Opération annulée.")
    else:
        init_db()