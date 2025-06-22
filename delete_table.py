import sqlite3

DB_PATH = "hotel.db"

def migrate_statut_colonne_et_update():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Ajouter la colonne statut, si elle n'existe pas
        try:
            cursor.execute("ALTER TABLE reservations ADD COLUMN statut TEXT DEFAULT 'réservée';")
            print("✅ Colonne 'statut' ajoutée avec succès.")
        except sqlite3.Error as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ La colonne 'statut' existe déjà, migration ignorée.")
            else:
                print(f"❌ Erreur lors de l'ajout de la colonne : {e}")
                return

        # Mettre à jour les statuts 'en cours' en 'réservée'
        cursor.execute("UPDATE reservations SET statut = 'réservée' WHERE statut = 'en cours';")
        print(f"✅ {cursor.rowcount} réservation(s) mise(s) à jour de 'en cours' à 'réservée'.")

        conn.commit()

    except sqlite3.Error as e:
        print(f"❌ Erreur base de données : {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    migrate_statut_colonne_et_update()
