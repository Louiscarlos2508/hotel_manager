# controllers/auth_controller.py
import sqlite3
from database.db import get_connection
import hashlib

def hash_password(pwd):
    return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute("SELECT id, username, role, nom_complet FROM users WHERE username=? AND password_hash=?", (username, password_hash))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "id": user[0],
            "username": user[1],
            "role": user[2],
            "nom_complet": user[3]
        }
    else:
        return None
