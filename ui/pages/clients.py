from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QFormLayout, QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from controllers.client_controller import ClientController


class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.client_actuel_id = None
        self.init_ui()
        self.charger_clients()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("Gestion des Clients")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Barre de recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom ou téléphone...")
        btn_search = QPushButton("Rechercher")
        btn_search.clicked.connect(self.rechercher_clients)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        # Tableau des clients
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom et Prénom", "Téléphone", "Email", "Nb réservations", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Formulaire de modification
        form_layout = QFormLayout()
        self.input_nom = QLineEdit()
        self.input_prenom = QLineEdit()
        self.input_tel = QLineEdit()
        self.input_email = QLineEdit()
        self.input_cni = QLineEdit()
        self.input_adresse = QLineEdit()

        form_layout.addRow("Nom *", self.input_nom)
        form_layout.addRow("Prénom", self.input_prenom)
        form_layout.addRow("Téléphone", self.input_tel)
        form_layout.addRow("Email", self.input_email)
        form_layout.addRow("CNI", self.input_cni)
        form_layout.addRow("Adresse", self.input_adresse)

        layout.addLayout(form_layout)

        # Bouton enregistrer
        self.btn_modifier = QPushButton("Enregistrer les modifications")
        self.btn_modifier.clicked.connect(self.enregistrer_modifications)
        layout.addWidget(self.btn_modifier)

    def charger_clients(self):
        """Charge les clients et leurs informations dans le tableau."""
        self.table.setRowCount(0)
        # La méthode du contrôleur est correcte
        result = ClientController.liste_clients_avec_reservations()

        if not result.get("success"):
            QMessageBox.warning(self, "Erreur", result.get("error", "Impossible de charger les clients."))
            return

        # --- CORRECTION ICI ---
        # On utilise la clé "data" et on ajoute .get("data", []) pour plus de sécurité
        clients = result.get("data", [])
        for row, client in enumerate(clients):
            # ... (le reste de votre méthode pour remplir le tableau est probablement correct)
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(client.get("id"))))
            self.table.setItem(row, 1, QTableWidgetItem(f"{client.get('nom', '')} {client.get('prenom', '')}".strip()))
            self.table.setItem(row, 2, QTableWidgetItem(client.get("tel", "")))
            self.table.setItem(row, 3, QTableWidgetItem(client.get("email", "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(client.get("nb_reservations", 0))))
            # Actions : Modifier + Supprimer si possible
            actions_widget = QWidget()
            layout = QHBoxLayout(actions_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            btn_modif = QPushButton("Modifier")
            btn_modif.clicked.connect(lambda _, c=client: self.charger_formulaire(c))
            layout.addWidget(btn_modif)

            if client.get("nb_reservations", 0) == 0:
                btn_suppr = QPushButton("Supprimer")
                btn_suppr.clicked.connect(lambda _, c=client: self.supprimer_client(c))
                layout.addWidget(btn_suppr)

            layout.addStretch()
            self.table.setCellWidget(row, 5, actions_widget)

    def supprimer_client(self, client):
        reply = QMessageBox.question(
            self, "Confirmer suppression",
            f"Voulez-vous vraiment supprimer le client {client['nom']} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            result = ClientController.supprimer_client(client["id"])
            if result["success"]:
                QMessageBox.information(self, "Succès", "Client supprimé avec succès.")
                self.charger_clients()
                self.client_actuel_id = None
                self.clear_formulaire()
            else:
                QMessageBox.warning(self, "Erreur", result.get("error", "Suppression échouée."))

    def clear_formulaire(self):
        self.input_nom.clear()
        self.input_prenom.clear()
        self.input_tel.clear()
        self.input_email.clear()
        self.input_cni.clear()
        self.input_adresse.clear()


    def charger_formulaire(self, client):
        self.client_actuel_id = client["id"]
        self.input_nom.setText(client.get("nom", ""))
        self.input_prenom.setText(client.get("prenom", ""))
        self.input_tel.setText(client.get("tel", ""))
        self.input_email.setText(client.get("email", ""))
        self.input_cni.setText(client.get("cni", ""))
        self.input_adresse.setText(client.get("adresse", ""))

    def enregistrer_modifications(self):
        if not self.client_actuel_id:
            QMessageBox.warning(self, "Erreur", "Aucun client sélectionné.")
            return

        result = ClientController.modifier_client(
            self.client_actuel_id,
            nom=self.input_nom.text(),
            prenom=self.input_prenom.text(),
            tel=self.input_tel.text(),
            email=self.input_email.text(),
            cni=self.input_cni.text(),
            adresse=self.input_adresse.text()
        )

        if result["success"]:
            QMessageBox.information(self, "Succès", "Client modifié avec succès.")
            self.charger_clients()
        else:
            QMessageBox.warning(self, "Erreur", result.get("error", "Modification échouée."))

    def rechercher_clients(self):
        recherche = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            item_nom = self.table.item(row, 0)
            item_tel = self.table.item(row, 2)

            visible = (
                recherche in (item_nom.text().lower() if item_nom else "") or
                recherche in (item_tel.text().lower() if item_tel else "")
            )
            self.table.setRowHidden(row, not visible)
