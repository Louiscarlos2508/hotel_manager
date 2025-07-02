-- SCHÉMA SQLite v1.3 - AVEC SOFT DELETE

-- 1. Types de chambres
CREATE TABLE types_chambre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    description TEXT,
    prix_par_nuit REAL NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Chambres
CREATE TABLE chambres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL UNIQUE,
    type_id INTEGER NOT NULL,
    statut TEXT NOT NULL CHECK(statut IN ('libre', 'occupée', 'en nettoyage', 'hors service')) DEFAULT 'libre',
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES types_chambre(id)
);

-- 3. Clients
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT,
    tel TEXT,
    email TEXT UNIQUE,
    cni TEXT,
    adresse TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Réservations
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    chambre_id INTEGER NOT NULL,
    date_arrivee DATE NOT NULL,
    date_depart DATE NOT NULL,
    statut TEXT NOT NULL CHECK(statut IN ('réservée', 'check-in', 'check-out', 'annulée')) DEFAULT 'réservée',
    nb_adultes INTEGER DEFAULT 1,
    nb_enfants INTEGER DEFAULT 0,
    prix_total_nuitee_estime REAL,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (chambre_id) REFERENCES chambres(id)
);

-- 5. Utilisateurs du système
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    nom_complet TEXT,
    actif BOOLEAN DEFAULT 1,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. Informations sur l'hôtel (n'a pas besoin de is_deleted, car il n'y a qu'une ligne)
CREATE TABLE hotel_info (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    nom TEXT NOT NULL,
    adresse TEXT,
    telephone TEXT,
    email TEXT,
    siret TEXT,
    tva_hebergement REAL NOT NULL DEFAULT 0.10,
    tva_restauration REAL NOT NULL DEFAULT 0.18,
    tdt_par_personne REAL NOT NULL DEFAULT 0.0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 7. Produits
CREATE TABLE produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    description TEXT,
    categorie TEXT NOT NULL CHECK(categorie IN ('Boisson chaude', 'Boisson fraîche', 'Alcool', 'Entrée', 'Plat', 'Dessert', 'Snack')),
    prix_unitaire REAL NOT NULL,
    disponible BOOLEAN DEFAULT 1,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. Commandes
CREATE TABLE commandes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    user_id_saisie INTEGER,
    date_commande DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut TEXT NOT NULL CHECK(statut IN ('Commandé', 'En cuisine', 'En livraison', 'Livré', 'Annulé')) DEFAULT 'Commandé',
    lieu_consommation TEXT CHECK(lieu_consommation IN ('Room Service', 'Bar', 'Restaurant')) DEFAULT 'Room Service',
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id),
    FOREIGN KEY (user_id_saisie) REFERENCES users(id)
);

-- 9. Commande Items (généralement, on ne les supprime pas individuellement, mais via la commande parente)
CREATE TABLE commande_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commande_id INTEGER NOT NULL,
    produit_id INTEGER NOT NULL,
    quantite INTEGER NOT NULL,
    prix_unitaire_capture REAL NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (commande_id) REFERENCES commandes(id) ON DELETE CASCADE,
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);

-- 10. Services Disponibles
CREATE TABLE services_disponibles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_service TEXT NOT NULL UNIQUE,
    description TEXT,
    prix REAL NOT NULL DEFAULT 0.0,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 11. Services Demandés
CREATE TABLE services_demandes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 1,
    prix_capture REAL NOT NULL,
    date_demande DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut TEXT NOT NULL CHECK(statut IN ('Demandé', 'En cours', 'Terminé')) DEFAULT 'Demandé',
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id),
    FOREIGN KEY (service_id) REFERENCES services_disponibles(id)
);

-- 12. Problèmes
CREATE TABLE problemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chambre_id INTEGER NOT NULL,
    signale_par_user_id INTEGER,
    description TEXT NOT NULL,
    date_signalement DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut TEXT NOT NULL CHECK(statut IN ('Nouveau', 'En cours', 'Résolu', 'Annulé')) DEFAULT 'Nouveau',
    priorite TEXT CHECK(priorite IN ('Basse', 'Moyenne', 'Haute')) DEFAULT 'Moyenne',
    date_resolution DATETIME,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chambre_id) REFERENCES chambres(id),
    FOREIGN KEY (signale_par_user_id) REFERENCES users(id)
);

-- 13. Factures (on ne les supprime généralement pas, on les annule)
CREATE TABLE factures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL UNIQUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    montant_total_ht REAL NOT NULL DEFAULT 0.0,
    montant_total_tva REAL NOT NULL DEFAULT 0.0,
    montant_total_ttc REAL NOT NULL DEFAULT 0.0,
    montant_paye REAL NOT NULL DEFAULT 0.0,
    statut TEXT NOT NULL CHECK(statut IN ('Brouillon', 'Finale', 'Payée', 'Partiellement payée', 'Annulée')) DEFAULT 'Brouillon',
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
);

-- 14. Facture Items (supprimés avec la facture)
CREATE TABLE facture_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 1,
    prix_unitaire_ht REAL NOT NULL,
    montant_ht REAL NOT NULL,
    montant_tva REAL NOT NULL,
    montant_ttc REAL NOT NULL,
    date_prestation DATE DEFAULT CURRENT_DATE,
    commande_id INTEGER,
    service_demande_id INTEGER,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facture_id) REFERENCES factures(id) ON DELETE CASCADE,
    FOREIGN KEY (commande_id) REFERENCES commandes(id),
    FOREIGN KEY (service_demande_id) REFERENCES services_demandes(id)
);

-- 15. Paiements (on ne les supprime généralement pas)
CREATE TABLE paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_id INTEGER NOT NULL,
    montant REAL NOT NULL,
    date_paiement DATETIME DEFAULT CURRENT_TIMESTAMP,
    methode TEXT CHECK(methode IN ('Carte de crédit', 'Espèces', 'Virement', 'Mobile Money', 'Autre')),
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facture_id) REFERENCES factures(id)
);

-- Les logs ne sont pas synchronisés
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    date_heure DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);