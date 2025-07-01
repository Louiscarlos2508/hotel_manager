-- =================================================================
--      SCHÉMA FINAL DE LA BASE DE DONNÉES HÔTELIÈRE (v1.1)
--      Avec contraintes d'intégrité et améliorations
-- =================================================================

-- 1. Types de chambres
-- Définit les catégories de chambres et leur prix de base.
CREATE TABLE types_chambre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    description TEXT,
    prix_par_nuit REAL NOT NULL
);

-- 2. Chambres
-- Liste toutes les chambres physiques de l'hôtel.
CREATE TABLE chambres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL UNIQUE,
    type_id INTEGER NOT NULL,
    -- La contrainte CHECK garantit la cohérence des statuts.
    statut TEXT NOT NULL CHECK(statut IN ('libre', 'occupée', 'en nettoyage', 'hors service')) DEFAULT 'libre',
    FOREIGN KEY (type_id) REFERENCES types_chambre(id)
);

-- 3. Clients
-- Informations sur les clients de l'hôtel.
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT,
    tel TEXT,
    -- L'email doit être unique pour éviter les doublons.
    email TEXT UNIQUE,
    cni TEXT,
    adresse TEXT
);

-- 4. Réservations
-- Enregistre les séjours des clients.
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    chambre_id INTEGER NOT NULL,
    date_arrivee DATE NOT NULL,
    date_depart DATE NOT NULL,
    -- Statuts clairs et standardisés pour le cycle de vie d'une réservation.
    statut TEXT NOT NULL CHECK(statut IN ('réservée', 'check-in', 'check-out', 'annulée')) DEFAULT 'réservée',
    nb_adultes INTEGER DEFAULT 1,
    nb_enfants INTEGER DEFAULT 0,
    prix_total_nuitee_estime REAL, -- Gardé comme estimation, la vérité est dans la facture.
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (chambre_id) REFERENCES chambres(id)
);

-- 5. Utilisateurs du système
-- Gère les accès du personnel à l'application.
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    nom_complet TEXT,
    actif BOOLEAN DEFAULT 1
);


-- 6. Logs d'audit
-- Trace les actions importantes effectuées dans le système.
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    -- Ajout de 'details' pour un contexte plus riche.
    details TEXT,
    date_heure DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 7. Informations sur l'hôtel
-- Données statiques sur l'établissement.
-- Dans schema_hotel.sql

-- 7. Informations sur l'hôtel
CREATE TABLE hotel_info (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    nom TEXT NOT NULL,
    adresse TEXT,
    telephone TEXT,
    email TEXT,
    siret TEXT,

    tva_hebergement REAL NOT NULL DEFAULT 0.10,
    tva_restauration REAL NOT NULL DEFAULT 0.18,
    tdt_par_personne REAL NOT NULL DEFAULT 0.0
);

-- 8. SYSTÈME UNIFIÉ : RESTAURATION & BOISSONS (F&B)
-- Le catalogue central de tous les produits vendus.
CREATE TABLE produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    description TEXT,
    categorie TEXT NOT NULL CHECK(categorie IN ('Boisson chaude', 'Boisson fraîche', 'Alcool', 'Entrée', 'Plat', 'Dessert', 'Snack')),
    prix_unitaire REAL NOT NULL,
    disponible BOOLEAN DEFAULT 1
);

-- Les commandes globales passées par les clients.
CREATE TABLE commandes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    user_id_saisie INTEGER,
    date_commande DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut TEXT NOT NULL CHECK(statut IN ('Commandé', 'En cuisine', 'En livraison', 'Livré', 'Annulé')) DEFAULT 'Commandé',
    lieu_consommation TEXT CHECK(lieu_consommation IN ('Room Service', 'Bar', 'Restaurant')) DEFAULT 'Room Service',
    FOREIGN KEY (reservation_id) REFERENCES reservations(id),
    FOREIGN KEY (user_id_saisie) REFERENCES users(id)
);

-- Le détail de chaque commande.
CREATE TABLE commande_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commande_id INTEGER NOT NULL,
    produit_id INTEGER NOT NULL,
    quantite INTEGER NOT NULL,
    prix_unitaire_capture REAL NOT NULL,
    FOREIGN KEY (commande_id) REFERENCES commandes(id) ON DELETE CASCADE,
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);

-- 9. SYSTÈME DE SERVICES CLIENTS
-- Catalogue des services additionnels (blanchisserie, etc.).
CREATE TABLE services_disponibles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_service TEXT NOT NULL UNIQUE,
    description TEXT,
    prix REAL NOT NULL DEFAULT 0.0
);

-- Journal des demandes de service par les clients.
CREATE TABLE services_demandes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 1,
    prix_capture REAL NOT NULL,
    date_demande DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut TEXT NOT NULL CHECK(statut IN ('Demandé', 'En cours', 'Terminé')) DEFAULT 'Demandé',
    FOREIGN KEY (reservation_id) REFERENCES reservations(id),
    FOREIGN KEY (service_id) REFERENCES services_disponibles(id)
);

-- 10. SYSTÈME DE MAINTENANCE / PROBLÈMES
-- Suivi des problèmes signalés dans les chambres.
CREATE TABLE problemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chambre_id INTEGER NOT NULL,
    signale_par_user_id INTEGER,
    description TEXT NOT NULL,
    date_signalement DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut TEXT NOT NULL CHECK(statut IN ('Nouveau', 'En cours', 'Résolu', 'Annulé')) DEFAULT 'Nouveau',
    priorite TEXT CHECK(priorite IN ('Basse', 'Moyenne', 'Haute')) DEFAULT 'Moyenne',
    date_resolution DATETIME,
    FOREIGN KEY (chambre_id) REFERENCES chambres(id),
    FOREIGN KEY (signale_par_user_id) REFERENCES users(id)
);

-- 11. NOUVEAU SYSTÈME DE FACTURATION INTÉGRÉ
-- La facture "conteneur" pour une réservation.
CREATE TABLE factures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL UNIQUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Champs détaillés pour une comptabilité précise
    montant_total_ht REAL NOT NULL DEFAULT 0.0,
    montant_total_tva REAL NOT NULL DEFAULT 0.0,
    montant_total_ttc REAL NOT NULL DEFAULT 0.0,
    montant_paye REAL NOT NULL DEFAULT 0.0,

    statut TEXT NOT NULL CHECK(statut IN ('Brouillon', 'Finale', 'Payée', 'Partiellement payée', 'Annulée')) DEFAULT 'Brouillon',
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
);

-- Chaque dépense (nuit, repas, service) est une ligne ici.
CREATE TABLE facture_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 1,

    -- Champs détaillés pour chaque ligne
    prix_unitaire_ht REAL NOT NULL,
    montant_ht REAL NOT NULL,
    montant_tva REAL NOT NULL,
    montant_ttc REAL NOT NULL,

    date_prestation DATE DEFAULT CURRENT_DATE,
    commande_id INTEGER,
    service_demande_id INTEGER,
    FOREIGN KEY (facture_id) REFERENCES factures(id) ON DELETE CASCADE,
    FOREIGN KEY (commande_id) REFERENCES commandes(id),
    FOREIGN KEY (service_demande_id) REFERENCES services_demandes(id)
);


-- Journal des paiements effectués pour une facture.
CREATE TABLE paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_id INTEGER NOT NULL,
    montant REAL NOT NULL,
    date_paiement DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Standardisation des méthodes de paiement.
    methode TEXT CHECK(methode IN ('Carte de crédit', 'Espèces', 'Virement', 'Autre')),
    FOREIGN KEY (facture_id) REFERENCES factures(id)
);