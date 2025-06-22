-- 1. Types de chambres
CREATE TABLE types_chambre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    description TEXT,
    prix_par_nuit REAL NOT NULL
);

-- 2. Chambres
CREATE TABLE chambres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL UNIQUE,
    type_id INTEGER NOT NULL,
    statut TEXT DEFAULT 'libre',
    FOREIGN KEY (type_id) REFERENCES types_chambre(id)
);

-- 3. Clients
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT,
    tel TEXT,
    email TEXT,
    cni TEXT,
    adresse TEXT
);

-- 4. Réservations
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    chambre_id INTEGER NOT NULL,
    date_arrivee DATE NOT NULL,
    date_depart DATE NOT NULL,
    statut TEXT DEFAULT 'réservée',
    nb_nuits INTEGER,
    prix_total_nuitee REAL,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (chambre_id) REFERENCES chambres(id)
);

-- 5. Consommations
CREATE TABLE consommations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    designation TEXT,
    quantite INTEGER DEFAULT 1,
    prix_unitaire REAL,
    date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id)
);

-- 6. Factures
CREATE TABLE factures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    montant_nuitee REAL,
    montant_consommation REAL,
    montant_total REAL,
    date_facture DATE DEFAULT CURRENT_DATE,
    statut_paiement TEXT DEFAULT 'non payé',
    methode_paiement TEXT,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id)
);


-- 7. Utilisateurs du système
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    nom_complet TEXT,
    actif BOOLEAN DEFAULT 1
);

-- 8. Logs
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    date_heure DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);



CREATE TABLE IF NOT EXISTS hotel_info (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    nom TEXT NOT NULL,
    adresse TEXT,
    telephone TEXT,
    email TEXT,
    siret TEXT
);



CREATE TABLE paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_id INTEGER NOT NULL,
    montant REAL NOT NULL,
    date_paiement DATETIME DEFAULT CURRENT_TIMESTAMP,
    methode TEXT,
    FOREIGN KEY (facture_id) REFERENCES factures(id)
);
