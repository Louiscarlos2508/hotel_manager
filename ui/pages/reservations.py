from collections import defaultdict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QComboBox, QDateEdit, QPushButton, QMessageBox,
    QLineEdit, QFormLayout, QGroupBox, QCheckBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem,
    QDialog, QSpinBox
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from controllers.reservation_controller import ReservationController
from controllers.client_controller import ClientController
from models.chambre_model import ChambreModel


class ReservationsPage(QWidget):
    def __init__(self, user_id=None):
        super().__init__()

        # Le contrôleur est notre unique point d'entrée pour les données de réservation
        self.reservation_controller = ReservationController(user_id)
        # Le modèle de chambre est seulement nécessaire pour le dialogue de création/modification
        self.chambre_model = ChambreModel()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # --- Configuration de l'interface (inchangée) ---
        title = QLabel("Gestion des Réservations")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.layout.addWidget(title)

        action_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Nouvelle réservation")
        btn_add.clicked.connect(self.open_reservation_dialog)
        action_layout.addWidget(btn_add)

        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.refresh_table)
        action_layout.addWidget(btn_refresh)

        search_label = QLabel("🔍 Rechercher :")
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Nom client, n° chambre, statut...")
        self.input_search.textChanged.connect(self.refresh_table)
        action_layout.addWidget(search_label)
        action_layout.addWidget(self.input_search)
        self.layout.addLayout(action_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Client", "Chambre", "Arrivée", "Départ", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.layout.addWidget(self.table)

        self.refresh_table()

    def open_reservation_dialog(self):
        # On passe les dépendances nécessaires au dialogue
        dialog = ReservationFormDialog(self, self.chambre_model, self.reservation_controller)
        if dialog.exec():
            self.refresh_table()

    def refresh_table(self):
        """
        Méthode ENTIÈREMENT RÉVISÉE pour être plus efficace et lisible.
        """
        try:
            # 1. UN SEUL APPEL pour récupérer toutes les données nécessaires
            response = self.reservation_controller.list_reservations()
            if not response.get("success"):
                QMessageBox.warning(self, "Erreur", response.get("error", "Erreur inconnue"))
                return

            all_reservations = response.get("data", [])

            # 2. FILTRAGE (recherche) sur les données déjà en mémoire
            search_text = self.input_search.text().lower().strip()
            if search_text:
                reservations_to_display = [
                    r for r in all_reservations
                    if search_text in r.get("client", "").lower()
                       or search_text in r.get("chambre", "").lower()
                       or search_text in r.get("statut", "").lower()
                       or search_text in r.get("date_arrivee", "")
                       or search_text in f"res-{r.get('id', '')}"
                ]
            else:
                reservations_to_display = all_reservations

            # 3. TRI et GROUPEMENT des données filtrées
            reservations_to_display.sort(key=lambda r: r["date_arrivee"], reverse=True)
            grouped = defaultdict(list)
            for r in reservations_to_display:
                grouped[r["date_arrivee"]].append(r)

            # 4. AFFICHAGE sans aucun appel supplémentaire à la base de données
            self.table.setRowCount(0)  # On vide la table avant de la remplir
            total_rows = len(reservations_to_display) + len(grouped)
            self.table.setRowCount(total_rows)

            current_row = 0
            for date_str, group in grouped.items():
                # Ligne de titre pour la date
                title_item = QTableWidgetItem(f"📅 Arrivées du {date_str}")
                title_item.setFlags(Qt.ItemIsEnabled)
                title_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                title_item.setBackground(Qt.lightGray)
                self.table.setSpan(current_row, 0, 1, self.table.columnCount())
                self.table.setItem(current_row, 0, title_item)
                current_row += 1

                # Lignes pour chaque réservation de ce groupe
                for r in group:
                    # On utilise directement les champs fournis par le modèle
                    self.table.setItem(current_row, 0, QTableWidgetItem(f"RES-{r['id']}"))
                    self.table.setItem(current_row, 1, QTableWidgetItem(r.get('client', 'N/A')))
                    self.table.setItem(current_row, 2, QTableWidgetItem(r.get('chambre', '?')))
                    self.table.setItem(current_row, 3, QTableWidgetItem(r.get('date_arrivee')))
                    self.table.setItem(current_row, 4, QTableWidgetItem(r.get('date_depart')))

                    statut = r.get("statut", "inconnu")
                    self.table.setItem(current_row, 5, QTableWidgetItem(statut.capitalize()))

                    # Création des boutons d'action
                    self.create_action_buttons(current_row, r['id'], statut)
                    current_row += 1

        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique",
                                 f"Une erreur est survenue lors du chargement des réservations : {e}")

    def create_action_buttons(self, row, reservation_id, statut):
        """Crée et place les boutons d'action dans une cellule de la table."""
        cell_widget = QWidget()
        h_layout = QHBoxLayout(cell_widget)
        h_layout.setContentsMargins(5, 0, 5, 0)
        h_layout.setSpacing(5)

        # Bouton Modifier (toujours visible sauf si annulée)
        if statut != "annulée" and statut != "check-out":
            btn_modifier = QPushButton("📝")
            btn_modifier.setToolTip("Modifier la réservation")
            btn_modifier.clicked.connect(lambda _, rid=reservation_id: self.modifier_reservation(rid))
            h_layout.addWidget(btn_modifier)

        # Bouton Annuler (visible seulement si 'réservée')
        if statut == "réservée":
            btn_annuler = QPushButton("❌")
            btn_annuler.setToolTip("Annuler la réservation")
            btn_annuler.clicked.connect(lambda _, rid=reservation_id: self.annuler_reservation(rid))
            h_layout.addWidget(btn_annuler)

        h_layout.addStretch()
        self.table.setCellWidget(row, 6, cell_widget)

    def modifier_reservation(self, reservation_id):
        # La logique de modification est complexe, la garder ici est acceptable
        # mais pourrait être déplacée dans une classe QDialog dédiée pour plus de clarté.
        try:
            res = self.reservation_controller.get_by_id(reservation_id)
            if not res.get("success"):
                QMessageBox.warning(self, "Erreur", res.get("error", "Réservation introuvable"))
                return

            # Le reste de votre logique de modification est bon...
            # ... (code de la méthode modifier_reservation inchangé)
            data = res["data"]
            current_chambre_id = data["chambre_id"]
            current_arrivee = QDate.fromString(data["date_arrivee"], "yyyy-MM-dd")
            current_depart = QDate.fromString(data["date_depart"], "yyyy-MM-dd")

            chambres_libres = [
                ch for ch in self.chambre_model.get_all()
                if ch["statut"] == "libre" or ch["id"] == current_chambre_id
            ]

            if not chambres_libres:
                QMessageBox.information(self, "Info", "Aucune chambre disponible pour modification.")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Modifier réservation #{reservation_id}")
            layout = QVBoxLayout(dialog)

            # ... (le reste du code de la boîte de dialogue de modification est correct)
            layout.addWidget(QLabel("Chambre :"))
            combo_chambres = QComboBox()
            id_to_index = {}
            for i, ch in enumerate(chambres_libres):
                combo_chambres.addItem(f"{ch['numero']} - {ch['prix_par_nuit']} FCFA/nuit", ch["id"])
                id_to_index[ch["id"]] = i
            combo_chambres.setCurrentIndex(id_to_index.get(current_chambre_id, 0))
            layout.addWidget(combo_chambres)

            layout.addWidget(QLabel("Date d'arrivée :"))
            date_arrivee_edit = QDateEdit(current_arrivee)
            date_arrivee_edit.setCalendarPopup(True)
            layout.addWidget(date_arrivee_edit)

            layout.addWidget(QLabel("Date de départ :"))
            date_depart_edit = QDateEdit(current_depart)
            date_depart_edit.setCalendarPopup(True)
            layout.addWidget(date_depart_edit)

            btn_layout = QHBoxLayout()
            btn_valider = QPushButton("Valider")
            btn_annuler = QPushButton("Annuler")
            btn_layout.addWidget(btn_valider)
            btn_layout.addWidget(btn_annuler)
            layout.addLayout(btn_layout)

            def valider():
                new_chambre_id = combo_chambres.currentData()
                new_arrivee = date_arrivee_edit.date()
                new_depart = date_depart_edit.date()

                if new_arrivee > new_depart:
                    QMessageBox.warning(dialog, "Erreur", "La date de départ doit être après la date d'arrivée.")
                    return

                try:
                    conflit = self.reservation_controller.check_conflit(
                        new_chambre_id, new_arrivee.toString("yyyy-MM-dd"), new_depart.toString("yyyy-MM-dd"),
                        exclude_id=reservation_id
                    )
                    if conflit:
                        QMessageBox.warning(dialog, "Conflit", "La chambre est déjà réservée sur cette période.")
                        return
                except Exception as e:
                    QMessageBox.warning(dialog, "Erreur", f"Erreur vérification disponibilité : {e}")
                    return

                update = self.reservation_controller.update(
                    reservation_id,
                    chambre_id=new_chambre_id,
                    date_arrivee=new_arrivee.toString("yyyy-MM-dd"),
                    date_depart=new_depart.toString("yyyy-MM-dd"),
                )
                if update.get("success"):
                    QMessageBox.information(dialog, "Succès", "Réservation modifiée avec succès.")
                    dialog.accept()
                    self.refresh_table()
                else:
                    QMessageBox.warning(dialog, "Erreur", update.get("error", "Erreur inconnue"))

            btn_valider.clicked.connect(valider)
            btn_annuler.clicked.connect(dialog.reject)

            dialog.setLayout(layout)
            dialog.setFixedSize(400, 300)
            dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def annuler_reservation(self, reservation_id):
        # Votre logique d'annulation est déjà très bonne.
        try:
            res = self.reservation_controller.get_by_id(reservation_id)
            if not res.get("success"):
                raise Exception(res.get("error", "Réservation introuvable"))

            statut = res.get("data", {}).get("statut", "")
            if statut != "réservée":
                QMessageBox.warning(self, "Annulation impossible",
                                    f"Seules les réservations avec le statut 'réservée' peuvent être annulées (statut actuel : '{statut}').")
                return

            confirm = QMessageBox.question(
                self, "Confirmation", "Annuler cette réservation ?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                cancel_res = self.reservation_controller.cancel(reservation_id)
                if cancel_res.get("success"):
                    QMessageBox.information(self, "Succès", "Réservation annulée.")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "Erreur", cancel_res.get("error", "Erreur lors de l'annulation."))

        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))


class ReservationFormDialog(QDialog):
    def __init__(self, parent, chambre_model, reservation_controller):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle réservation")
        self.chambre_model = chambre_model
        self.reservation_controller = reservation_controller

        layout = QVBoxLayout(self)

        # --- Groupe Client (inchangé) ---
        client_group = QGroupBox("Client")
        client_layout = QFormLayout()
        self.checkbox_new_client = QCheckBox("Nouveau client")
        self.checkbox_new_client.setChecked(True)
        self.checkbox_new_client.stateChanged.connect(self.toggle_client_mode)
        client_layout.addRow(self.checkbox_new_client)
        self.combo_clients = QComboBox()
        self.load_clients()
        client_layout.addRow("Client existant :", self.combo_clients)
        self.input_nom = QLineEdit()
        self.input_prenom = QLineEdit()
        self.input_tel = QLineEdit()
        self.input_email = QLineEdit()
        self.input_cni = QLineEdit()
        self.input_adresse = QLineEdit()
        client_layout.addRow("Nom * :", self.input_nom)
        client_layout.addRow("Prénom :", self.input_prenom)
        client_layout.addRow("Téléphone * :", self.input_tel)
        client_layout.addRow("Email * :", self.input_email)
        client_layout.addRow("CNI * :", self.input_cni)
        client_layout.addRow("Adresse :", self.input_adresse)
        client_group.setLayout(client_layout)
        layout.addWidget(client_group)

        # --- Groupe Réservation (MODIFIÉ pour être plus clair et inclure les nouveaux champs) ---
        resa_group = QGroupBox("Détails de la réservation")
        form_layout = QFormLayout()  # Utilisation d'un QFormLayout pour un meilleur alignement

        self.combo_chambres = QComboBox()
        self.load_chambres()
        form_layout.addRow("Chambre :", self.combo_chambres)

        self.date_arrivee = QDateEdit(QDate.currentDate())
        self.date_arrivee.setCalendarPopup(True)
        form_layout.addRow("Date d'arrivée :", self.date_arrivee)

        self.date_depart = QDateEdit(QDate.currentDate().addDays(1))
        self.date_depart.setCalendarPopup(True)
        form_layout.addRow("Date de départ :", self.date_depart)

        # --- AJOUT : Champs pour adultes et enfants ---
        self.spin_adultes = QSpinBox()
        self.spin_adultes.setRange(1, 10)  # De 1 à 10 adultes
        self.spin_adultes.setValue(1)
        form_layout.addRow("Nombre d'adultes :", self.spin_adultes)

        self.spin_enfants = QSpinBox()
        self.spin_enfants.setRange(0, 10)  # De 0 à 10 enfants
        form_layout.addRow("Nombre d'enfants :", self.spin_enfants)

        resa_group.setLayout(form_layout)
        layout.addWidget(resa_group)
        # --- FIN DES MODIFICATIONS ---

        prix_layout = QHBoxLayout()
        self.label_prix_nuit = QLabel("Prix par nuit : 0 FCFA")
        self.label_nb_nuits = QLabel("Nombre de nuits : 0")
        self.label_prix_total = QLabel("Prix total : 0 FCFA")
        prix_layout.addWidget(self.label_prix_nuit)
        prix_layout.addWidget(self.label_nb_nuits)
        prix_layout.addWidget(self.label_prix_total)
        layout.addLayout(prix_layout)

        self.combo_chambres.currentIndexChanged.connect(self.update_prix)
        self.date_arrivee.dateChanged.connect(self.update_prix)
        self.date_depart.dateChanged.connect(self.update_prix)

        btn_reserver = QPushButton("Réserver")
        btn_reserver.clicked.connect(self.action_reserver)
        layout.addWidget(btn_reserver)

        self.toggle_client_mode()
        self.update_prix()
        self.setFixedSize(600, 550) # Augmenter un peu la hauteur pour les nouveaux champs

    def toggle_client_mode(self):
        nouveau = self.checkbox_new_client.isChecked()
        self.combo_clients.setEnabled(not nouveau)
        for widget in [self.input_nom, self.input_prenom, self.input_tel, self.input_email, self.input_cni,
                       self.input_adresse]:
            widget.setEnabled(nouveau)

    def load_clients(self):
        self.combo_clients.clear()
        try:
            res = ClientController.liste_clients()
            if not res.get("success", False):
                raise Exception(res.get("error", "Erreur chargement clients"))

            # --- CORRECTION ICI ---
            # On utilise la clé "data" au lieu de "clients"
            clients_data = res.get("data", [])
            for c in clients_data:
                self.combo_clients.addItem(f"{c.get('nom', '')} {c.get('prenom', '')}".strip(), c.get("id"))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur chargement clients : {e}")


    def load_chambres(self):
        self.combo_chambres.clear()
        try:
            for chambre in self.chambre_model.get_all():
                if chambre['statut'] == 'libre':
                    self.combo_chambres.addItem(f"N° {chambre['numero']} - {chambre['prix_par_nuit']} FCFA/nuit",
                                                chambre['id'])
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur chargement chambres : {e}")

    def update_prix(self):
        chambre_id = self.combo_chambres.currentData()
        if chambre_id is None:
            self.label_prix_nuit.setText("Prix par nuit : 0 FCFA")
            self.label_nb_nuits.setText("Nombre de nuits : 0")
            self.label_prix_total.setText("Prix total : 0 FCFA")
            return
        try:
            chambre = self.chambre_model.get_by_id(chambre_id)
            prix_nuit = chambre['prix_par_nuit']
            nb_nuits = self.date_arrivee.date().daysTo(self.date_depart.date())
            if nb_nuits <= 0:
                nb_nuits = 1
            prix_total = nb_nuits * prix_nuit
            self.label_prix_nuit.setText(f"Prix par nuit : {prix_nuit:,.0f} FCFA")
            self.label_nb_nuits.setText(f"Nombre de nuits : {nb_nuits}")
            self.label_prix_total.setText(f"Prix total : {prix_total:,.0f} FCFA")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur calcul prix : {e}")

    def action_reserver(self):
        chambre_id = self.combo_chambres.currentData()
        if chambre_id is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une chambre.")
            return

        date_arrivee_qdate = self.date_arrivee.date()
        date_depart_qdate = self.date_depart.date()

        if date_arrivee_qdate < QDate.currentDate():
            QMessageBox.warning(self, "Erreur", "La date d'arrivée ne peut pas être dans le passé.")
            return

        if date_depart_qdate < date_arrivee_qdate:
            QMessageBox.warning(self, "Erreur", "La date de départ doit être après la date d'arrivée.")
            return

        date_arrivee = date_arrivee_qdate.toString("yyyy-MM-dd")
        date_depart = date_depart_qdate.toString("yyyy-MM-dd")

        try:
            if self.reservation_controller.check_conflit(chambre_id, date_arrivee, date_depart):
                QMessageBox.warning(self, "Conflit", "La chambre est déjà réservée sur cette période.")
                return
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur vérification disponibilité : {e}")
            return

        if self.checkbox_new_client.isChecked():
            nom = self.input_nom.text().strip()
            if not nom:
                QMessageBox.warning(self, "Erreur", "Le nom du client est obligatoire.")
                return
            result_client = ClientController.ajouter_client(
                nom, self.input_prenom.text().strip(), self.input_tel.text().strip(),
                self.input_email.text().strip(), self.input_cni.text().strip(), self.input_adresse.text().strip())
            if not result_client.get("success", False):
                QMessageBox.warning(self, "Erreur",
                                    f"Erreur création client : {result_client.get('error', 'Erreur inconnue')}")
                return
            client_id = result_client.get("id")
        else:
            client_id = self.combo_clients.currentData()
            if client_id is None:
                QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un client.")
                return

        try:
            result = self.reservation_controller.create(
                client_id, chambre_id, date_arrivee, date_depart
            )
            if not result.get("success", False):
                QMessageBox.warning(self, "Erreur",
                                    f"Erreur création réservation : {result.get('error', 'Erreur inconnue')}")
                return
            reservation_id = result.get("reservation_id")
            QMessageBox.information(self, "Succès", f"Réservation créée avec l'ID {reservation_id}")
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la création de réservation : {e}")
