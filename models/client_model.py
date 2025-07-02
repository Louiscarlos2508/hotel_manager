# /home/soutonnoma/PycharmProjects/HotelManger/models/client_model.py
import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from models.base_model import BaseModel

class ClientModel(BaseModel):
    """Modèle pour gérer les clients dans la base de données."""

    @classmethod
    def create(cls, nom: str, prenom: Optional[str] = None, tel: Optional[str] = None,
               email: Optional[str] = None, cni: Optional[str] = None, adresse: Optional[str] = None) -> int:
        query = """
            INSERT INTO clients (nom, prenom, tel, email, cni, adresse)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            nom.strip() if isinstance(nom, str) else nom,
            prenom.strip() if isinstance(prenom, str) else prenom,
            tel.strip() if isinstance(tel, str) else tel,
            email.strip() if isinstance(email, str) else email,
            cni.strip() if isinstance(cni, str) else cni,
            adresse.strip() if isinstance(adresse, str) else adresse,
        )
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, params)
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception("Un client avec ces informations (tél/email/CNI) existe déjà.") from e
        except sqlite3.Error as e:
            raise Exception(f"Erreur base de données lors de la création du client : {e}") from e

    @classmethod
    def get_by_id(cls, client_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM clients WHERE id = ? AND is_deleted = 0"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (client_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Erreur de récupération du client {client_id} : {e}") from e

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        query = "SELECT * FROM clients WHERE is_deleted = 0 ORDER BY nom, prenom"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur de récupération de tous les clients : {e}") from e

    @classmethod
    def update(cls, client_id: int, **kwargs) -> bool:
        fields_to_update = {k: v.strip() if isinstance(v, str) else v for k, v in kwargs.items() if v is not None}
        if not fields_to_update:
            return True

        fields_to_update['updated_at'] = datetime.now(timezone.utc).isoformat()

        set_clause = ", ".join([f"{key} = ?" for key in fields_to_update])
        query = f"UPDATE clients SET {set_clause} WHERE id = ? AND is_deleted = 0"
        params = list(fields_to_update.values()) + [client_id]

        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError as e:
            raise Exception("La mise à jour a échoué, informations en conflit (tél/email/CNI).") from e
        except sqlite3.Error as e:
            raise Exception(f"Erreur de mise à jour du client {client_id} : {e}") from e

    @classmethod
    def delete(cls, client_id: int) -> bool:
        if cls.has_reservations(client_id):
            raise Exception("Impossible de supprimer un client avec des réservations existantes.")
        query = "UPDATE clients SET is_deleted = 1, updated_at = ? WHERE id = ?"
        timestamp_actuel = datetime.now(timezone.utc).isoformat()
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (timestamp_actuel, client_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Erreur de suppression du client {client_id} : {e}") from e

    @classmethod
    def has_reservations(cls, client_id: int) -> bool:
        query = "SELECT 1 FROM reservations WHERE client_id = ? AND statut IN ('réservée', 'check-in') AND is_deleted = 0 LIMIT 1"
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query, (client_id,))
                return cur.fetchone() is not None
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la vérification des réservations pour le client {client_id} : {e}") from e


    @classmethod
    def get_all_with_reservation_count(cls) -> List[Dict[str, Any]]:
        query = """
            SELECT c.*, COUNT(r.id) AS nb_reservations
            FROM clients c
            LEFT JOIN reservations r ON c.id = r.client_id
            WHERE c.is_deleted = 0
            GROUP BY c.id
            ORDER BY c.nom, c.prenom
        """
        try:
            with cls.connect() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur de récupération des clients avec le compte des réservations : {e}") from e