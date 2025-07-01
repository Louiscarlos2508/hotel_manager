# /home/soutonnoma/PycharmProjects/HotelManger/ui/pages/produit.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QHBoxLayout, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QTextEdit
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from controllers.produit_controller import ProduitController

# Catégories définies dans le schéma de la base de données
CATEGORIES_PRODUITS = ['Boisson chaude', 'Boisson fraîche', 'Alcool', 'Entrée', 'Plat', 'Dessert', 'Snack']


class ProduitsPage(QWidget):
    """
    Page principale pour la gestion des produits (CRUD).
    """

    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_produits()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Gestion des Produits et Services")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        layout.addWidget(title)

        # Actions
        action_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.load_produits)
        btn_ajouter = QPushButton("➕ Nouveau Produit")
        btn_ajouter.clicked.connect(self.open_add_dialog)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom ou catégorie...")
        self.search_input.textChanged.connect(self.filter_table)

        action_layout.addWidget(btn_refresh)
        action_layout.addWidget(btn_ajouter)
        action_layout.addStretch()
        action_layout.addWidget(QLabel("🔍"))
        action_layout.addWidget(self.search_input)
        layout.addLayout(action_layout)

        # Tableau des produits
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Catégorie", "Prix Unitaire", "Disponible", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    def load_produits(self):
        """Charge tous les produits depuis la base de données et remplit le tableau."""
        self.table.setRowCount(0)
        result = ProduitController.liste_produits()

        if not result.get("success"):
            QMessageBox.warning(self, "Erreur", result.get("error", "Impossible de charger les produits."))
            return

        produits = result.get("data", [])
        for row, produit in enumerate(produits):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(produit.get("id"))))
            self.table.setItem(row, 1, QTableWidgetItem(produit.get("nom")))
            self.table.setItem(row, 2, QTableWidgetItem(produit.get("categorie")))
            self.table.setItem(row, 3, QTableWidgetItem(f"{produit.get('prix_unitaire', 0):,.0f} FCFA"))

            disponible_item = QTableWidgetItem("Oui" if produit.get("disponible") else "Non")
            disponible_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, disponible_item)

            self.create_action_buttons(row, produit.get("id"))

        self.filter_table()  # Appliquer le filtre de recherche actuel

    def create_action_buttons(self, row, produit_id):
        """Crée les boutons d'action pour une ligne du tableau."""
        cell_widget = QWidget()
        h_layout = QHBoxLayout(cell_widget)
        h_layout.setContentsMargins(5, 0, 5, 0)
        h_layout.setSpacing(5)

        btn_modifier = QPushButton("📝 Modifier")
        btn_modifier.clicked.connect(lambda _, pid=produit_id: self.open_edit_dialog(pid))
        h_layout.addWidget(btn_modifier)

        btn_supprimer = QPushButton("🗑️ Supprimer")
        btn_supprimer.clicked.connect(lambda _, pid=produit_id: self.delete_produit(pid))
        h_layout.addWidget(btn_supprimer)

        self.table.setCellWidget(row, 5, cell_widget)

    def open_add_dialog(self):
        """Ouvre le formulaire pour ajouter un nouveau produit."""
        dialog = ProduitFormDialog(self)
        if dialog.exec():
            self.load_produits()

    def open_edit_dialog(self, produit_id):
        """Ouvre le formulaire pour modifier un produit existant."""
        dialog = ProduitFormDialog(self, produit_id=produit_id)
        if dialog.exec():
            self.load_produits()

    def delete_produit(self, produit_id):
        """Supprime un produit après confirmation."""
        confirm = QMessageBox.question(self, "Confirmation",
                                       f"Voulez-vous vraiment supprimer le produit ID {produit_id} ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            result = ProduitController.supprimer_produit(produit_id)
            if result.get("success"):
                QMessageBox.information(self, "Succès", "Produit supprimé avec succès.")
                self.load_produits()
            else:
                QMessageBox.warning(self, "Erreur", result.get("error", "La suppression a échoué."))

    def filter_table(self):
        """Filtre les lignes du tableau en fonction du texte de recherche."""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            nom_item = self.table.item(row, 1)
            categorie_item = self.table.item(row, 2)

            nom_matches = search_text in nom_item.text().lower() if nom_item else False
            categorie_matches = search_text in categorie_item.text().lower() if categorie_item else False

            self.table.setRowHidden(row, not (nom_matches or categorie_matches))


class ProduitFormDialog(QDialog):
    """
    Formulaire pour la création et la modification de produits.
    """

    def __init__(self, parent=None, produit_id=None):
        super().__init__(parent)
        self.produit_id = produit_id
        self.is_edit_mode = produit_id is not None

        self.setWindowTitle("Modifier le Produit" if self.is_edit_mode else "Nouveau Produit")
        self.setMinimumWidth(400)

        self.init_form()
        if self.is_edit_mode:
            self.load_produit_data()

    def init_form(self):
        layout = QFormLayout(self)

        self.nom_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(80)
        self.categorie_combo = QComboBox()
        self.categorie_combo.addItems(CATEGORIES_PRODUITS)
        self.prix_spinbox = QDoubleSpinBox()
        self.prix_spinbox.setRange(0, 1_000_000)
        self.prix_spinbox.setSuffix(" FCFA")
        self.disponible_check = QCheckBox("Le produit est disponible à la vente")
        self.disponible_check.setChecked(True)

        layout.addRow("Nom *:", self.nom_input)
        layout.addRow("Description:", self.desc_input)
        layout.addRow("Catégorie *:", self.categorie_combo)
        layout.addRow("Prix Unitaire *:", self.prix_spinbox)
        layout.addRow(self.disponible_check)

        # Boutons
        button_layout = QHBoxLayout()
        btn_save = QPushButton("Enregistrer")
        btn_save.clicked.connect(self.save_produit)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_cancel)
        layout.addRow(button_layout)

    def load_produit_data(self):
        """Charge les données du produit à modifier dans le formulaire."""
        result = ProduitController.obtenir_produit(self.produit_id)
        if result.get("success"):
            produit = result["data"]
            self.nom_input.setText(produit.get("nom", ""))
            self.desc_input.setText(produit.get("description", ""))
            self.categorie_combo.setCurrentText(produit.get("categorie", ""))
            self.prix_spinbox.setValue(produit.get("prix_unitaire", 0))
            self.disponible_check.setChecked(produit.get("disponible", True))
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de charger les données du produit.")
            self.reject()

    def save_produit(self):
        """Sauvegarde les données du produit (création ou modification)."""
        nom = self.nom_input.text().strip()
        if not nom:
            QMessageBox.warning(self, "Validation", "Le nom du produit est obligatoire.")
            return

        data = {
            "nom": nom,
            "description": self.desc_input.toPlainText().strip(),
            "categorie": self.categorie_combo.currentText(),
            "prix_unitaire": self.prix_spinbox.value(),
            "disponible": self.disponible_check.isChecked()
        }

        if self.is_edit_mode:
            result = ProduitController.modifier_produit(self.produit_id, **data)
        else:
            result = ProduitController.ajouter_produit(**data)

        if result.get("success"):
            QMessageBox.information(self, "Succès", "Produit enregistré avec succès.")
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", result.get("error", "L'enregistrement a échoué."))
