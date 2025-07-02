# /home/soutonnoma/PycharmProjects/HotelManager/services/sync_service.py

import os
import sqlite3
from datetime import datetime, timezone
from supabase import create_client, Client
from models.base_model import DB_PATH

# Vos clés Supabase
SUPABASE_URL = "https://jsrxilcgklprmnbmijjh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpzcnhpbGNna2xwcm1uYm1pampoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MDk2MDksImV4cCI6MjA2Njk4NTYwOX0.ehsgzdH_2wfJGtOxgTtHhJiCFvy050lsSd2yckIQNxw"

# Liste des tables à synchroniser
TABLES_TO_SYNC = [
    'types_chambre', 'chambres', 'clients', 'reservations', 'hotel_info',
    'produits', 'commandes', 'commande_items', 'services_disponibles',
    'services_demandes', 'problemes', 'factures', 'facture_items', 'paiements',
    'users'
]


class SyncService:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.last_sync_file = os.path.join(os.path.dirname(DB_PATH), ".last_sync")

    def _get_last_sync_time(self) -> str:
        try:
            with open(self.last_sync_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "1970-01-01T00:00:00+00:00"

    def _set_last_sync_time(self, sync_time: str):
        with open(self.last_sync_file, 'w') as f:
            f.write(sync_time)

    def _get_local_db_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def synchronize(self):
        print(f"[{datetime.now()}] Lancement de la synchronisation...")
        try:
            current_sync_time = datetime.now(timezone.utc).isoformat()
            last_sync_time = self._get_last_sync_time()

            print(f"  > Dernière synchro : {last_sync_time}")

            self.sync_up(last_sync_time)
            self.sync_down(last_sync_time)

            self._set_last_sync_time(current_sync_time)
            print(f"[{datetime.now()}] Synchronisation terminée avec succès.")
            return {"success": True}
        except Exception as e:
            print(f"ERREUR CRITIQUE DE SYNCHRONISATION : {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def sync_up(self, last_sync_time: str):
        """Synchronise les données locales modifiées vers Supabase."""
        print("  [↑] Phase de synchronisation montante (local -> supabase)...")
        conn = self._get_local_db_connection()
        cursor = conn.cursor()

        for table in TABLES_TO_SYNC:
            try:
                cursor.execute(f"SELECT * FROM {table} WHERE updated_at > ?", (last_sync_time,))
                local_changes = [dict(row) for row in cursor.fetchall()]

                if local_changes:
                    print(f"    - {len(local_changes)} changement(s) trouvé(s) dans la table '{table}'.")
                    self.supabase.table(table).upsert(local_changes).execute()

            except sqlite3.OperationalError as e:
                print(f"    - AVERTISSEMENT: La table '{table}' ou la colonne 'updated_at' n'existe pas localement. Ignorée. ({e})")

        conn.close()

    def sync_down(self, last_sync_time: str):
        """Synchronise les données de Supabase modifiées vers la base locale."""
        print("  [↓] Phase de synchronisation descendante (supabase -> local)...")
        conn = self._get_local_db_connection()
        cursor = conn.cursor()

        for table in TABLES_TO_SYNC:
            try:
                response = self.supabase.table(table).select("*").gt("updated_at", last_sync_time).execute()
                remote_changes = response.data

                if remote_changes:
                    print(f"    - {len(remote_changes)} changement(s) à appliquer pour la table '{table}'.")
                    for record in remote_changes:
                        # On nettoie les champs que SQLite ne comprendrait pas
                        record.pop('created_at', None)

                        # --- CORRECTION ---
                        # On ne retire PLUS le hash du mot de passe.
                        # Il est nécessaire pour créer de nouveaux utilisateurs synchronisés.
                        # La sécurité est assurée par le fait que c'est un hash et que la connexion est HTTPS.

                        columns = ', '.join(record.keys())
                        placeholders = ', '.join(['?'] * len(record))

                        # INSERT OR REPLACE est l'équivalent SQLite de l'upsert
                        query = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
                        cursor.execute(query, tuple(record.values()))
            except Exception as e:
                 print(f"    - ERREUR: Impossible de synchroniser la table '{table}' depuis Supabase. ({e})")

        conn.commit()
        conn.close()