import sqlite3

def ajouter_colonnes_facturation(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Colonnes à ajouter pour la table "factures"
    colonnes_factures = [
        ("montant_total_ht", "REAL", 0.0),
        ("montant_total_tva", "REAL", 0.0),
        ("montant_total_ttc", "REAL", 0.0)
    ]

    # 2. Colonnes à ajouter pour la table "facture_items"
    colonnes_facture_items = [
        ("prix_unitaire_ht", "REAL", 0.0),
        ("montant_ht", "REAL", 0.0),
        ("montant_tva", "REAL", 0.0),
        ("montant_ttc", "REAL", 0.0)
    ]

    def ajouter_colonnes_si_absentes(nom_table, colonnes):
        cursor.execute(f"PRAGMA table_info({nom_table})")
        colonnes_existantes = [col[1] for col in cursor.fetchall()]

        for nom_col, type_sql, defaut in colonnes:
            if nom_col not in colonnes_existantes:
                print(f"Ajout de la colonne '{nom_col}' dans '{nom_table}'...")
                cursor.execute(f"""
                    ALTER TABLE {nom_table} 
                    ADD COLUMN {nom_col} {type_sql} NOT NULL DEFAULT {defaut}
                """)
            else:
                print(f"La colonne '{nom_col}' existe déjà dans '{nom_table}'.")

    # Appliquer la migration aux deux tables
    ajouter_colonnes_si_absentes("factures", colonnes_factures)
    ajouter_colonnes_si_absentes("facture_items", colonnes_facture_items)

    conn.commit()
    conn.close()
    print("✅ Migration des taxes de facturation terminée.")

# --- À exécuter ---
#if __name__ == "__main__":
    #chemin_db = "hotel.db"  # <-- Remplace ce chemin
    #ajouter_colonnes_facturation(chemin_db)
