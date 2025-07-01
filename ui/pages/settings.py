from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QTextEdit, QDoubleSpinBox,
    QMessageBox, QHeaderView, QGroupBox, QFormLayout
)
from PySide6.QtGui import QFont
from controllers.types_chambre_controller import TypesChambreController
from controllers.hotel_info_controller import HotelInfoController  # à créer


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paramètres de l'hôtel")
        self.resize(800, 600)
        main_layout = QVBoxLayout(self)

        title = QLabel("Paramètres de l'hôtel")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        main_layout.addWidget(title)

        # Section Infos Hôtel
        self.group_hotel = QGroupBox("Informations et Fiscalité")
        hotel_layout = QFormLayout(self.group_hotel)
        self.input_nom = QLineEdit()
        self.input_adresse = QLineEdit()
        self.input_telephone = QLineEdit()
        self.input_email = QLineEdit()
        self.input_siret = QLineEdit()

        hotel_layout.addRow("Nom de l'hôtel :", self.input_nom)
        hotel_layout.addRow("Adresse :", self.input_adresse)
        hotel_layout.addRow("Téléphone :", self.input_telephone)
        hotel_layout.addRow("Email :", self.input_email)
        hotel_layout.addRow("SIRET :", self.input_siret)

        # Champs pour la TVA (inchangés)
        self.input_tva_hebergement = QDoubleSpinBox()
        self.input_tva_hebergement.setSuffix(" %")
        self.input_tva_hebergement.setRange(0, 100)
        self.input_tva_hebergement.setDecimals(2)
        self.input_tva_restauration = QDoubleSpinBox()
        self.input_tva_restauration.setSuffix(" %")
        self.input_tva_restauration.setRange(0, 100)
        self.input_tva_restauration.setDecimals(2)
        hotel_layout.addRow("TVA Hébergement :", self.input_tva_hebergement)
        hotel_layout.addRow("TVA Bar & Restaurant :", self.input_tva_restauration)

        # --- NOUVEAU : Champ pour la TDT ---
        self.input_tdt = QDoubleSpinBox()
        self.input_tdt.setSuffix(" FCFA")
        self.input_tdt.setRange(0, 10000)  # Montant max par personne
        self.input_tdt.setDecimals(0)
        hotel_layout.addRow("Taxe de séjour (TDT) / pers / nuit :", self.input_tdt)
        # --- FIN DE LA NOUVEAUTÉ ---

        self.btn_save_hotel = QPushButton("Enregistrer les informations")
        self.btn_save_hotel.clicked.connect(self.save_hotel_info)
        hotel_layout.addRow(self.btn_save_hotel)
        main_layout.addWidget(self.group_hotel)

        # Section Types de chambre
        self.group_types = QGroupBox("Types de chambres")
        types_layout = QVBoxLayout(self.group_types)

        # Tableau des types
        self.table_types = QTableWidget(0, 4)
        self.table_types.setHorizontalHeaderLabels(["ID", "Nom", "Description", "Prix/nuit"])
        self.table_types.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_types.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_types.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_types.itemSelectionChanged.connect(self.on_type_selected)
        types_layout.addWidget(self.table_types)

        # Formulaire ajout/modif type
        form_layout = QHBoxLayout()
        self.input_type_nom = QLineEdit()
        self.input_type_nom.setPlaceholderText("Nom")
        self.input_type_desc = QTextEdit()
        self.input_type_desc.setPlaceholderText("Description")
        self.input_type_desc.setFixedHeight(50)
        self.input_type_prix = QDoubleSpinBox()
        self.input_type_prix.setPrefix("CFA ")
        self.input_type_prix.setRange(0, 1000000)
        self.input_type_prix.setSingleStep(1000)
        self.input_type_prix.setDecimals(2)
        self.input_type_prix.setSingleStep(1)
        form_layout.addWidget(self.input_type_nom)
        form_layout.addWidget(self.input_type_desc)
        form_layout.addWidget(self.input_type_prix)
        types_layout.addLayout(form_layout)

        # Boutons CRUD
        btn_layout = QHBoxLayout()
        self.btn_add_type = QPushButton("Ajouter")
        self.btn_edit_type = QPushButton("Modifier")
        self.btn_delete_type = QPushButton("Supprimer")
        self.btn_edit_type.setEnabled(False)
        self.btn_delete_type.setEnabled(False)
        btn_layout.addWidget(self.btn_add_type)
        btn_layout.addWidget(self.btn_edit_type)
        btn_layout.addWidget(self.btn_delete_type)
        types_layout.addLayout(btn_layout)

        main_layout.addWidget(self.group_types)

        # Connexions boutons
        self.btn_add_type.clicked.connect(self.add_type)
        self.btn_edit_type.clicked.connect(self.edit_type)
        self.btn_delete_type.clicked.connect(self.delete_type)

        self.selected_type_id = None

        # Charger données
        self.load_hotel_info()
        self.load_types()

    def load_hotel_info(self):
        res = HotelInfoController.get_info()
        if res.get("success") and res.get("data"):
            info = res["data"]
            self.input_nom.setText(info.get("nom", ""))
            self.input_adresse.setText(info.get("adresse", ""))
            self.input_telephone.setText(info.get("telephone", ""))
            self.input_email.setText(info.get("email", ""))
            self.input_siret.setText(info.get("siret", ""))

            self.input_tva_hebergement.setValue(info.get("tva_hebergement", 0.10) * 100)
            self.input_tva_restauration.setValue(info.get("tva_restauration", 0.18) * 100)

            # --- MODIFICATION : Charger la TDT ---
            self.input_tdt.setValue(info.get("tdt_par_personne", 0))
        else:
            self.input_tva_hebergement.setValue(10.0)
            self.input_tva_restauration.setValue(18.0)
            self.input_tdt.setValue(0)

    def save_hotel_info(self):
        nom = self.input_nom.text().strip()
        adresse = self.input_adresse.text().strip()
        telephone = self.input_telephone.text().strip()
        email = self.input_email.text().strip()
        siret = self.input_siret.text().strip()

        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de l'hôtel est obligatoire.")
            return

        tva_hebergement = self.input_tva_hebergement.value() / 100.0
        tva_restauration = self.input_tva_restauration.value() / 100.0

        # --- MODIFICATION : Récupérer la TDT ---
        tdt_par_personne = self.input_tdt.value()

        res = HotelInfoController.save_info(
            nom, adresse, telephone, email, siret,
            tva_hebergement, tva_restauration, tdt_par_personne
        )

        if res.get("success"):
            QMessageBox.information(self, "Succès", "Informations de l'hôtel enregistrées.")
        else:
            QMessageBox.warning(self, "Erreur", res.get("error"))

    def load_types(self):
        self.table_types.setRowCount(0)
        res = TypesChambreController.lister_types()
        if not res["success"]:
            QMessageBox.warning(self, "Erreur", res["error"])
            return
        for t in res["data"]:
            row = self.table_types.rowCount()
            self.table_types.insertRow(row)
            self.table_types.setItem(row, 0, QTableWidgetItem(str(t["id"])))
            self.table_types.setItem(row, 1, QTableWidgetItem(t["nom"]))
            self.table_types.setItem(row, 2, QTableWidgetItem(t.get("description", "")))
            item_prix = QTableWidgetItem(f"FCFA {t['prix_par_nuit']:.2f}")
            item_prix.setData(Qt.UserRole, t['prix_par_nuit'])  # Stocke le float en data
            self.table_types.setItem(row, 3, item_prix)

    def clear_type_form(self):
        self.input_type_nom.clear()
        self.input_type_desc.clear()
        self.input_type_prix.setValue(0)
        self.selected_type_id = None
        self.btn_edit_type.setEnabled(False)
        self.btn_delete_type.setEnabled(False)
        self.btn_add_type.setEnabled(True)

    def on_type_selected(self):
        selected = self.table_types.selectedItems()
        if not selected:
            self.clear_type_form()
            return
        row = selected[0].row()
        self.selected_type_id = int(self.table_types.item(row, 0).text())
        self.input_type_nom.setText(self.table_types.item(row, 1).text())
        self.input_type_desc.setText(self.table_types.item(row, 2).text())

        # Récupérer le prix depuis Qt.UserRole (float stocké)
        prix = self.table_types.item(row, 3).data(Qt.UserRole)
        if prix is not None:
            self.input_type_prix.setValue(float(prix))
        else:
            self.input_type_prix.setValue(0)

        self.btn_edit_type.setEnabled(True)
        self.btn_delete_type.setEnabled(True)
        self.btn_add_type.setEnabled(False)

    def validate_type_form(self):
        nom = self.input_type_nom.text().strip()
        prix = self.input_type_prix.value()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return False
        if prix <= 0:
            QMessageBox.warning(self, "Erreur", "Le prix par nuit doit être supérieur à 0.")
            return False
        return True

    def add_type(self):
        if not self.validate_type_form():
            return
        nom = self.input_type_nom.text().strip()
        desc = self.input_type_desc.toPlainText().strip()
        prix = self.input_type_prix.value()
        res = TypesChambreController.ajouter_type(nom, desc, prix)
        if res["success"]:
            QMessageBox.information(self, "Succès", res["message"])
            self.load_types()
            self.clear_type_form()
        else:
            QMessageBox.warning(self, "Erreur", res["error"])

    def edit_type(self):
        if not self.validate_type_form():
            return
        if not self.selected_type_id:
            QMessageBox.warning(self, "Erreur", "Aucun type sélectionné.")
            return
        nom = self.input_type_nom.text().strip()
        desc = self.input_type_desc.toPlainText().strip()
        prix = self.input_type_prix.value()
        res = TypesChambreController.modifier_type(self.selected_type_id, nom, desc, prix)
        if res["success"]:
            QMessageBox.information(self, "Succès", res["message"])
            self.load_types()
            self.clear_type_form()
        else:
            QMessageBox.warning(self, "Erreur", res["error"])

    def delete_type(self):
        if not self.selected_type_id:
            QMessageBox.warning(self, "Erreur", "Aucun type sélectionné.")
            return
        confirm = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment supprimer ce type de chambre ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            res = TypesChambreController.supprimer_type(self.selected_type_id)
            if res["success"]:
                QMessageBox.information(self, "Succès", res["message"])
                self.load_types()
                self.clear_type_form()
            else:
                QMessageBox.warning(self, "Erreur", res["error"])
