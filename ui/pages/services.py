from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTabWidget, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout,
                               QMessageBox, QDialog, QFormLayout, QLineEdit,
                               QTextEdit, QDoubleSpinBox, QDialogButtonBox,
                               QSpinBox, QComboBox, QInputDialog)  # Importer QInputDialog
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from controllers.reservation_controller import ReservationController
# Importer les contrôleurs
from controllers.service_demande_controller import ServiceDemandeController
from controllers.service_disponible_controller import ServiceDisponibleController


class ServicesPage(QWidget):
    def __init__(self, current_user_role: str):
        super().__init__()
        self.current_user_role = current_user_role

        # Layout principal
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Titre de la page
        title = QLabel("Gestion des Services Clients")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Système d'onglets
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Création des onglets
        self.creer_onglet_demandes()

        # L'onglet de gestion du catalogue n'est créé que pour l'admin
        if self.current_user_role == 'admin':
            self.creer_onglet_catalogue()

    def creer_onglet_demandes(self):
        """Crée l'onglet pour gérer les demandes de service (pour Réception et Admin)."""
        demandes_widget = QWidget()
        layout = QVBoxLayout(demandes_widget)

        # Tableau pour afficher les demandes
        self.table_demandes = QTableWidget()
        self.table_demandes.setColumnCount(7)
        self.table_demandes.setHorizontalHeaderLabels([
            "ID Demande", "ID Réservation", "Nom Service", "Quantité",
            "Prix Capturé (CFA)", "Date", "Statut"
        ])
        self.table_demandes.setColumnHidden(0, True)  # Masquer l'ID technique
        self.table_demandes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_demandes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_demandes.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table_demandes)

        # Boutons d'action
        buttons_layout = QHBoxLayout()
        btn_nouvelle_demande = QPushButton("➕ Nouvelle Demande")

        # Le bouton est visible et utilisable par la réception et l'admin
        if self.current_user_role == 'reception':
            buttons_layout.addWidget(btn_nouvelle_demande)

        btn_changer_statut = QPushButton("🔄 Changer Statut")
        btn_supprimer_demande = QPushButton("❌ Supprimer la Demande")

        buttons_layout.addWidget(btn_changer_statut)
        buttons_layout.addWidget(btn_supprimer_demande)
        layout.addLayout(buttons_layout)

        # Connexion des signaux
        btn_nouvelle_demande.clicked.connect(self.ouvrir_formulaire_nouvelle_demande)
        btn_changer_statut.clicked.connect(self.changer_statut_demande)
        btn_supprimer_demande.clicked.connect(self.supprimer_demande)

        self.tabs.addTab(demandes_widget, "Gestion des Demandes")
        self.charger_donnees_demandes()

    def creer_onglet_catalogue(self):
        """Crée l'onglet pour gérer le catalogue des services (Admin seulement)."""
        catalogue_widget = QWidget()
        layout = QVBoxLayout(catalogue_widget)

        # Tableau pour afficher les services disponibles
        self.table_catalogue = QTableWidget()
        self.table_catalogue.setColumnCount(4)
        self.table_catalogue.setHorizontalHeaderLabels(["ID", "Nom du Service", "Description", "Prix Unitaire (CFA)"])
        self.table_catalogue.setColumnHidden(0, True)  # Masquer l'ID technique

        self.table_catalogue.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_catalogue.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_catalogue.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table_catalogue)

        # Boutons d'action
        buttons_layout = QHBoxLayout()
        btn_ajouter = QPushButton("➕ Ajouter un Service")
        btn_modifier = QPushButton("✏️ Modifier le Service")
        btn_supprimer = QPushButton("❌ Supprimer le Service")

        buttons_layout.addWidget(btn_ajouter)
        buttons_layout.addWidget(btn_modifier)
        buttons_layout.addWidget(btn_supprimer)
        layout.addLayout(buttons_layout)

        # Connexion des signaux
        btn_ajouter.clicked.connect(self.ajouter_service_catalogue)
        btn_modifier.clicked.connect(self.modifier_service_catalogue)
        btn_supprimer.clicked.connect(self.supprimer_service_catalogue)

        self.tabs.addTab(catalogue_widget, "Catalogue des Services (Admin)")
        self.charger_donnees_catalogue()

    # --- Méthodes pour l'onglet "Gestion des Demandes" ---

    def charger_donnees_demandes(self):
        # Pour avoir le nom du service, il faudrait modifier le modèle ServiceDemandeModel
        # pour y inclure une jointure avec services_disponibles.
        result = ServiceDemandeController.lister_toutes_les_demandes()
        if result["success"]:
            demandes = result["data"]
            self.table_demandes.setRowCount(len(demandes))
            for row, demande in enumerate(demandes):
                self.table_demandes.setItem(row, 0, QTableWidgetItem(str(demande['id'])))
                self.table_demandes.setItem(row, 1, QTableWidgetItem(str(demande['reservation_id'])))
                # Idéalement, le modèle renverrait 'nom_service'
                self.table_demandes.setItem(row, 2, QTableWidgetItem(
                    demande.get('nom_service', f"Service ID: {demande['service_id']}")))
                self.table_demandes.setItem(row, 3, QTableWidgetItem(str(demande['quantite'])))
                self.table_demandes.setItem(row, 4, QTableWidgetItem(f"{demande['prix_capture']:,.0f}"))
                self.table_demandes.setItem(row, 5, QTableWidgetItem(demande['date_demande']))
                self.table_demandes.setItem(row, 6, QTableWidgetItem(demande['statut']))
        else:
            QMessageBox.warning(self, "Erreur", result["error"])

    def ouvrir_formulaire_nouvelle_demande(self):
        dialog = NouvelleDemandeDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data:  # Si get_data retourne None (erreur de validation)
                return

            result = ServiceDemandeController.creer_demande(**data)
            if result["success"]:
                QMessageBox.information(self, "Succès", result["message"])
                self.charger_donnees_demandes()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])

    def changer_statut_demande(self):
        selected_rows = self.table_demandes.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner une demande.")
            return

        row = selected_rows[0].row()
        demande_id = int(self.table_demandes.item(row, 0).text())
        current_statut = self.table_demandes.item(row, 6).text()

        statuts_possibles = ["Demandé", "En cours", "Terminé"]

        nouveau_statut, ok = QInputDialog.getItem(self, "Changer le statut",
                                                  "Choisissez le nouveau statut :",
                                                  statuts_possibles,
                                                  statuts_possibles.index(current_statut), False)

        if ok and nouveau_statut:
            result = ServiceDemandeController.changer_statut(demande_id, nouveau_statut)
            if result["success"]:
                self.charger_donnees_demandes()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])

    def supprimer_demande(self):
        selected_rows = self.table_demandes.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner une demande.")
            return

        row = selected_rows[0].row()
        demande_id = int(self.table_demandes.item(row, 0).text())
        confirm = QMessageBox.question(self, "Confirmation", "Supprimer cette demande ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            result = ServiceDemandeController.supprimer_demande(demande_id)
            if result["success"]:
                self.charger_donnees_demandes()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])

    # --- Méthodes pour l'onglet "Catalogue des Services" (Admin) ---

    def charger_donnees_catalogue(self):
        if not hasattr(self, 'table_catalogue'): return
        result = ServiceDisponibleController.lister_services()
        if result["success"]:
            services = result["data"]
            self.table_catalogue.setRowCount(len(services))
            for row, service in enumerate(services):
                self.table_catalogue.setItem(row, 0, QTableWidgetItem(str(service['id'])))
                self.table_catalogue.setItem(row, 1, QTableWidgetItem(service['nom_service']))
                self.table_catalogue.setItem(row, 2, QTableWidgetItem(service['description']))
                self.table_catalogue.setItem(row, 3, QTableWidgetItem(f"{service['prix']:,.0f}"))
        else:
            QMessageBox.warning(self, "Erreur", result["error"])

    def ajouter_service_catalogue(self):
        dialog = NouveauServiceDialog(None, self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['nom_service']:
                QMessageBox.warning(self, "Erreur", "Le nom du service est obligatoire.")
                return
            result = ServiceDisponibleController.ajouter_service(**data)
            if result["success"]:
                self.charger_donnees_catalogue()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])

    def modifier_service_catalogue(self):
        selected_rows = self.table_catalogue.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un service.")
            return

        row = selected_rows[0].row()
        service = {
            "id": int(self.table_catalogue.item(row, 0).text()),
            "nom_service": self.table_catalogue.item(row, 1).text(),
            "description": self.table_catalogue.item(row, 2).text(),
            "prix": float(self.table_catalogue.item(row, 3).text().replace(',', ''))
        }
        dialog = NouveauServiceDialog(service, self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['nom_service']:
                QMessageBox.warning(self, "Erreur", "Le nom du service est obligatoire.")
                return
            result = ServiceDisponibleController.modifier_service(service["id"], **data)
            if result["success"]:
                self.charger_donnees_catalogue()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])

    def supprimer_service_catalogue(self):
        selected_rows = self.table_catalogue.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un service.")
            return

        row = selected_rows[0].row()
        service_id = int(self.table_catalogue.item(row, 0).text())
        confirm = QMessageBox.question(self, "Confirmation", "Supprimer ce service ?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            result = ServiceDisponibleController.supprimer_service(service_id)
            if result["success"]:
                self.charger_donnees_catalogue()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])


class NouveauServiceDialog(QDialog):
    def __init__(self, service=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Service" if not service else "Modifier le Service")
        self.service = service
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.nom_input = QLineEdit(service["nom_service"] if service else "")
        self.desc_input = QTextEdit(service["description"] if service else "")
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setRange(0, 10000000)
        self.prix_input.setDecimals(0)
        self.prix_input.setGroupSeparatorShown(True)
        if service:
            self.prix_input.setValue(service["prix"])

        form.addRow("Nom du service:", self.nom_input)
        form.addRow("Description:", self.desc_input)
        form.addRow("Prix unitaire (CFA):", self.prix_input)

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "nom_service": self.nom_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "prix": self.prix_input.value()
        }


class NouvelleDemandeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle Demande de Service")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.combo_reservation = QComboBox()
        self.combo_service = QComboBox()
        self.spin_quantite = QSpinBox()
        self.spin_quantite.setRange(1, 100)

        self.services = {}
        self._load_data()

        form.addRow("Réservation:", self.combo_reservation)
        form.addRow("Service:", self.combo_service)
        form.addRow("Quantité:", self.spin_quantite)

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_data(self):
        # Récupérer uniquement les réservations avec statut "check-in"
        res_reservations = ReservationController.list_reservations(filtre={"statuts": ["check-in"]})
        if res_reservations.get("success"):
            for r in res_reservations["data"]:
                self.combo_reservation.addItem(f"Résa n°{r['id']} - {r['client']}", r['id'])
        else:
            error_msg = res_reservations.get("error", "Erreur inconnue.")
            QMessageBox.warning(self, "Erreur de chargement", f"Impossible de charger les réservations:\n{error_msg}")
            self.combo_reservation.addItem("Erreur de chargement", -1)
            self.combo_reservation.setEnabled(False)

        # Chargement des services (inchangé)
        res_services = ServiceDisponibleController.lister_services()
        if res_services.get("success"):
            for s in res_services["data"]:
                label = f"{s['nom_service']} ({s['prix']:,.0f} CFA)"
                self.combo_service.addItem(label, s["id"])
                self.services[s["id"]] = s
        else:
            error_msg = res_services.get("error", "Erreur inconnue.")
            QMessageBox.warning(self, "Erreur de chargement", f"Impossible de charger les services:\n{error_msg}")
            self.combo_service.addItem("Erreur de chargement", -1)
            self.combo_service.setEnabled(False)

    def get_data(self):
        service_id = self.combo_service.currentData()
        reservation_id = self.combo_reservation.currentData()

        if service_id is None or service_id == -1 or reservation_id is None or reservation_id == -1:
            QMessageBox.warning(self, "Données invalides",
                                "Veuillez sélectionner une réservation et un service valides.")
            return None

        quantite = self.spin_quantite.value()
        prix_unitaire = self.services[service_id]["prix"]
        return {
            "reservation_id": reservation_id,
            "service_id": service_id,
            "quantite": quantite,
            "prix_capture": quantite * prix_unitaire
        }