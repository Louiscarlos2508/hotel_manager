from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QHBoxLayout, QLineEdit, QComboBox,
    QMessageBox, QGroupBox, QFormLayout
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from controllers.chambre_controller import ChambreController
from models.types_chambre_model import TypesChambreModel


class RoomsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
                margin-top: 15px;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        title = QLabel("Gestion des chambres")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.layout.addWidget(title)

        # Bouton Ajouter
        self.btn_add = QPushButton("Ajouter une chambre")
        self.btn_add.clicked.connect(self.toggle_add_form)
        self.layout.addWidget(self.btn_add, alignment=Qt.AlignLeft)

        # Formulaire (caché par défaut)
        self.add_group = QGroupBox("Ajouter une nouvelle chambre")
        self.add_group.hide()
        form_layout = QFormLayout()

        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Ex: 101")
        form_layout.addRow("Numéro de chambre :", self.input_numero)

        self.select_type = QComboBox()
        self.type_map = {}
        types = TypesChambreModel.get_all()
        if types:
            self.type_map = {t["nom"]: t["id"] for t in types}
            self.select_type.addItems(self.type_map.keys())
        form_layout.addRow("Type de chambre :", self.select_type)

        self.select_statut = QComboBox()
        self.select_statut.addItems(["libre", "occupée", "en maintenance"])
        form_layout.addRow("Statut :", self.select_statut)

        btns = QHBoxLayout()
        self.btn_create = QPushButton("Créer")
        self.btn_create.clicked.connect(self.create_chambre)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.toggle_add_form)
        btns.addWidget(self.btn_create)
        btns.addWidget(btn_cancel)
        form_layout.addRow(btns)

        self.add_group.setLayout(form_layout)
        self.layout.addWidget(self.add_group)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Numéro", "Type", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.load_data()

    def toggle_add_form(self):
        visible = self.add_group.isVisible()
        self.add_group.setVisible(not visible)
        self.btn_add.setText("Fermer le formulaire" if not visible else "Ajouter une chambre")

    def load_data(self):
        self.table.setRowCount(0)
        result = ChambreController.get_all_chambres()
        if not result["success"]:
            QMessageBox.warning(self, "Erreur", result["error"])
            return

        chambres = result["data"]
        for row, chambre in enumerate(chambres):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(chambre["numero"])))
            self.table.setItem(row, 1, QTableWidgetItem(chambre["type_nom"]))
            self.table.setItem(row, 2, QTableWidgetItem(chambre["statut"]))

            btn_edit = QPushButton("Modifier")
            btn_edit.setEnabled(True)
            btn_edit.clicked.connect(lambda _, c=chambre: self.edit_chambre(c))

            btn_delete = QPushButton("Supprimer")
            btn_delete.clicked.connect(lambda _, cid=chambre["id"]: self.delete_chambre(cid))

            action_layout = QHBoxLayout()
            action_layout.setAlignment(Qt.AlignCenter)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            container = QWidget()
            container.setLayout(action_layout)
            self.table.setCellWidget(row, 3, container)

    def create_chambre(self):
        numero = self.input_numero.text().strip()
        type_nom = self.select_type.currentText()
        type_id = self.type_map.get(type_nom)
        statut = self.select_statut.currentText()

        if not numero:
            QMessageBox.warning(self, "Erreur", "Le numéro de chambre est requis.")
            return

        result = ChambreController.create_chambre(numero, type_id, statut)
        if not result["success"]:
            QMessageBox.warning(self, "Erreur", result["error"])
            return

        QMessageBox.information(self, "Succès", "Chambre ajoutée avec succès.")
        self.input_numero.clear()
        self.toggle_add_form()
        self.load_data()

    def delete_chambre(self, chambre_id):
        confirm = QMessageBox.question(self, "Confirmation", "Supprimer cette chambre ?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            result = ChambreController.delete_chambre(chambre_id)
            if result["success"]:
                QMessageBox.information(self, "Succès", "Chambre supprimée.")
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])

    def edit_chambre(self, chambre):
        self.toggle_add_form()
        self.btn_add.setText("Fermer le formulaire")
        self.add_group.setTitle("Modifier la chambre")

        # Remplir le formulaire avec les données de la chambre
        self.input_numero.setText(str(chambre["numero"]))

        # Remplir type
        nom_type = chambre["type_nom"]
        index = self.select_type.findText(nom_type)
        if index >= 0:
            self.select_type.setCurrentIndex(index)

        # Remplir statut
        index_statut = self.select_statut.findText(chambre["statut"])
        if index_statut >= 0:
            self.select_statut.setCurrentIndex(index_statut)

        # Remplacer le signal du bouton "Créer" par "Modifier"
        try:
            self.btn_create.clicked.disconnect()
        except:
            pass

        self.btn_create.setText("Modifier")
        self.btn_create.clicked.connect(lambda: self.update_chambre(chambre["id"]))

    def update_chambre(self, chambre_id):
        numero = self.input_numero.text().strip()
        type_nom = self.select_type.currentText()
        type_id = self.type_map.get(type_nom)
        statut = self.select_statut.currentText()

        if not numero:
            QMessageBox.warning(self, "Erreur", "Le numéro de chambre est requis.")
            return

        result = ChambreController.update_chambre(chambre_id, numero, type_id, statut)
        if not result["success"]:
            QMessageBox.warning(self, "Erreur", result["error"])
            return

        QMessageBox.information(self, "Succès", "Chambre modifiée avec succès.")
        self.input_numero.clear()
        self.btn_create.setText("Créer")
        self.btn_create.clicked.disconnect()
        self.btn_create.clicked.connect(self.create_chambre)
        self.toggle_add_form()
        self.load_data()

