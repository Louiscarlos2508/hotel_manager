import sqlite3
import hashlib

def hash_password(pwd):
    return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

conn = sqlite3.connect('hotel.db')
cursor = conn.cursor()

username = "bar"
password = "bar123"
password_hash = hash_password(password)
role = "bar"
nom_complet = "Barman"

# Vérifier si l'utilisateur existe déjà (optionnel)
cursor.execute("SELECT id FROM users WHERE username=?", (username,))
if cursor.fetchone():
    print("Utilisateur admin déjà présent.")
else:
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, nom_complet)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, role, nom_complet))
    conn.commit()
    print("Utilisateur " + username + " ajouté avec succès.")

conn.close()
