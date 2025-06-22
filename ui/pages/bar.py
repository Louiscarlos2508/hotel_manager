from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QMessageBox, QSpinBox, QDoubleSpinBox, QComboBox
)
from PySide6.QtGui import QFont
from controllers.consommation_controller import ConsommationController
from controllers.reservation_controller import ReservationController  # pour récupérer les réservations
from database.db import get_connection


class BarPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.consommation_actuelle_id = None  # ID en cours de modification

        title = QLabel("Bar - Gestion des consommations")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        layout.addWidget(title)

        # Formulaire ajout consommation
        form_layout = QHBoxLayout()

        # Choix réservation (id + info simple)
        form_layout.addWidget(QLabel("Réservation:"))
        self.combo_reservations = QComboBox()
        self.load_reservations()
        form_layout.addWidget(self.combo_reservations)

        # Désignation
        form_layout.addWidget(QLabel("Désignation:"))
        self.input_designation = QLineEdit()
        form_layout.addWidget(self.input_designation)

        # Quantité
        form_layout.addWidget(QLabel("Quantité:"))
        self.input_quantite = QSpinBox()
        self.input_quantite.setMinimum(1)
        self.input_quantite.setValue(1)
        form_layout.addWidget(self.input_quantite)

        # Prix unitaire
        form_layout.addWidget(QLabel("Prix unitaire:"))
        self.input_prix_unitaire = QDoubleSpinBox()
        self.input_prix_unitaire.setMinimum(0)
        self.input_prix_unitaire.setMaximum(1000000)
        self.input_prix_unitaire.setDecimals(2)
        form_layout.addWidget(self.input_prix_unitaire)

        # Bouton ajouter
        self.btn_add = QPushButton("Ajouter")
        self.btn_add.clicked.connect(self.add_consommation)
        form_layout.addWidget(self.btn_add)

        layout.addLayout(form_layout)

        # Tableau consommations
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Réservation ID", "Désignation", "Quantité", "Prix unitaire", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.load_consommations()

    def load_reservations(self):
        self.combo_reservations.clear()
        try:
            conn = get_connection()
            controller = ReservationController(conn)

            # On filtre uniquement les réservations en cours
            result = controller.list_reservations(filtre={"statut": "en cours"})
            if not result.get("success", False):
                QMessageBox.warning(self, "Erreur",
                                    f"Erreur chargement réservations : {result.get('error', 'Erreur inconnue')}")
                return

            reservations = result.get("data", [])

            for res in reservations:
                # Affiche ID + numéro de chambre
                text = f"ID {res['id']} - Chambre {res['chambre_numero']}"
                self.combo_reservations.addItem(text, res['id'])

            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur chargement réservations : {e}")

    def load_consommations(self):
        self.table.setRowCount(0)
        try:
            response = ConsommationController.get_all_consommations()
            if response.get("success"):
                consommations = response.get("data", [])
            else:
                consommations = []
                QMessageBox.warning(self, "Erreur", response.get("error", "Erreur inconnue"))
        except Exception as e:
            consommations = []
            QMessageBox.warning(self, "Erreur", f"Erreur chargement consommations : {e}")

        for row, conso in enumerate(consommations):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(conso["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(conso["reservation_id"])))
            self.table.setItem(row, 2, QTableWidgetItem(conso["designation"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(conso["quantite"])))
            self.table.setItem(row, 4, QTableWidgetItem(f"{conso['prix_unitaire']:.2f}"))

            action_layout = QHBoxLayout()
            widget_action = QWidget()

            btn_edit = QPushButton("Modifier")
            btn_edit.clicked.connect(lambda _, c=conso: self.charger_formulaire_conso(c))
            action_layout.addWidget(btn_edit)

            btn_delete = QPushButton("Supprimer")
            btn_delete.clicked.connect(lambda _, cid=conso["id"]: self.delete_consommation(cid))
            action_layout.addWidget(btn_delete)

            action_layout.setContentsMargins(0, 0, 0, 0)
            widget_action.setLayout(action_layout)
            self.table.setCellWidget(row, 5, widget_action)

    def charger_formulaire_conso(self, conso):
        self.consommation_actuelle_id = conso["id"]
        self.input_designation.setText(conso["designation"])
        self.input_quantite.setValue(conso["quantite"])
        self.input_prix_unitaire.setValue(conso["prix_unitaire"])

        index = self.combo_reservations.findData(conso["reservation_id"])
        if index >= 0:
            self.combo_reservations.setCurrentIndex(index)

        self.btn_add.setText("Modifier")

    def add_consommation(self):
        reservation_id = self.combo_reservations.currentData()
        designation = self.input_designation.text().strip()
        quantite = self.input_quantite.value()
        prix_unitaire = self.input_prix_unitaire.value()

        if reservation_id is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une réservation valide.")
            return

        if not designation:
            QMessageBox.warning(self, "Erreur", "La désignation est obligatoire.")
            return

        self.btn_add.setEnabled(False)

        try:
            if self.consommation_actuelle_id is not None:
                # Mode modification
                result = ConsommationController.update_consommation(
                    self.consommation_actuelle_id, reservation_id, designation, quantite, prix_unitaire
                )
                if result.get("success"):
                    QMessageBox.information(self, "Succès", "Consommation modifiée.")
                else:
                    QMessageBox.warning(self, "Erreur", result.get("error", "Erreur modification"))
            else:
                # Mode ajout
                result = ConsommationController.add_consommation(
                    reservation_id, designation, quantite, prix_unitaire
                )
                if result.get("success"):
                    QMessageBox.information(self, "Succès", "Consommation ajoutée.")
                else:
                    QMessageBox.warning(self, "Erreur", result.get("error", "Erreur ajout"))

            # Réinitialise le formulaire
            self.input_designation.clear()
            self.input_quantite.setValue(1)
            self.input_prix_unitaire.setValue(0.0)
            self.combo_reservations.setCurrentIndex(0)
            self.consommation_actuelle_id = None
            self.btn_add.setText("Ajouter")
            self.load_consommations()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur consommation : {e}")
        finally:
            self.btn_add.setEnabled(True)

    def delete_consommation(self, consommation_id):
        confirm = QMessageBox.question(self, "Confirmer", "Supprimer cette consommation ?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                ConsommationController.delete_consommation(consommation_id)
                QMessageBox.information(self, "Succès", "Consommation supprimée.")
                self.load_consommations()
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Erreur suppression consommation : {e}")
