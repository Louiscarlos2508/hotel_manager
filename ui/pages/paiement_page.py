from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QFormLayout, QDoubleSpinBox, QComboBox, QPushButton, QMessageBox
)

from controllers.consommation_controller import ConsommationController
from controllers.facture_controller import FactureController
from controllers.paiement_controller import PaiementController
from database.db import get_connection


class PaiementPage(QWidget):
    def __init__(self, reservation_id):
        super().__init__()
        self.reservation_id = reservation_id
        self.facture = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.label_total = QLabel("Montant total: ...")
        self.label_paye = QLabel("Montant payé: ...")
        self.label_reste = QLabel("Reste à payer: ...")

        layout.addWidget(self.label_total)
        layout.addWidget(self.label_paye)
        layout.addWidget(self.label_reste)
        self.label_prix_par_nuit = QLabel("Prix par nuit: ...")
        self.label_total_hebergement = QLabel("Total hébergement: ...")

        layout.addWidget(self.label_prix_par_nuit)
        layout.addWidget(self.label_total_hebergement)

        # Liste des consommations
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Désignation", "Quantité", "Total"])
        layout.addWidget(QLabel("Détails des consommations:"))
        layout.addWidget(self.table)

        # Paiement
        form = QFormLayout()
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setMaximum(10000000)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(2)

        self.input_methode = QComboBox()
        self.input_methode.addItems(["Espèces", "Carte", "Mobile Money", "Autre"])

        form.addRow("Montant à encaisser:", self.input_montant)
        form.addRow("Méthode de paiement:", self.input_methode)
        layout.addLayout(form)

        self.btn_enregistrer = QPushButton("Enregistrer le paiement")
        self.btn_enregistrer.clicked.connect(self.enregistrer_paiement)
        layout.addWidget(self.btn_enregistrer)

        # Liste des paiements
        self.table_paiements = QTableWidget()
        self.table_paiements.setColumnCount(2)
        self.table_paiements.setHorizontalHeaderLabels(["Montant", "Méthode"])
        layout.addWidget(QLabel("Historique des paiements:"))
        layout.addWidget(self.table_paiements)

    def load_data(self):
        facture = FactureController.get_facture_by_reservation(self.reservation_id)
        if not facture:
            # Créer la facture pour la réservation
            conn = get_connection()
            resp = FactureController.create_facture_auto(self.reservation_id)
            conn.close()

            if not resp["success"]:
                QMessageBox.critical(self, "Erreur", resp.get("error", "Erreur création facture"))
                return
            facture = resp["data"]

        self.facture = facture

        # Affichage hébergement
        from controllers.reservation_controller import ReservationController
        from controllers.chambre_controller import ChambreController

        reservation = ReservationController.get_by_id(self.reservation_id)
        chambre = ChambreController.get_chambre_by_id(reservation["chambre_id"])["data"]

        prix_par_nuit = chambre["prix_par_nuit"]
        date_arrivee = datetime.fromisoformat(reservation["date_arrivee"]).date()
        date_depart = datetime.fromisoformat(reservation["date_depart"]).date()
        nb_nuits = (date_depart - date_arrivee).days
        if nb_nuits <= 0:
            nb_nuits = 1

        total_hebergement = prix_par_nuit * nb_nuits

        self.label_prix_par_nuit.setText(f"Prix par nuit: {prix_par_nuit} FCFA")
        self.label_total_hebergement.setText(f"Total hébergement: {total_hebergement} FCFA")

        # Chargement consommations
        resp = ConsommationController.get_consommations_by_reservation(self.reservation_id)
        if resp.get("success"):
            consommations = resp.get("data", [])
            self.table.setRowCount(0)
            for c in consommations:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(c["designation"]))
                self.table.setItem(row, 1, QTableWidgetItem(str(c["quantite"])))
                total = c["quantite"] * c["prix_unitaire"]
                self.table.setItem(row, 2, QTableWidgetItem(str(total)))

        # Paiements existants
        paiements = PaiementController.get_paiements_par_facture(self.facture["id"])
        self.refresh_paiements(paiements)

    def refresh_paiements(self, paiements):
        self.table_paiements.setRowCount(0)
        total_paye = 0
        for p in paiements:
            row = self.table_paiements.rowCount()
            self.table_paiements.insertRow(row)
            self.table_paiements.setItem(row, 0, QTableWidgetItem(str(p["montant"])))
            self.table_paiements.setItem(row, 1, QTableWidgetItem(p["methode"]))
            total_paye += p["montant"]

        montant_total = self.facture["montant_total"]
        reste = montant_total - total_paye

        self.label_total.setText(f"Montant total: {montant_total} FCFA")
        self.label_paye.setText(f"Montant payé: {total_paye} FCFA")
        self.label_reste.setText(f"Reste à payer: {reste} FCFA")

        self.btn_enregistrer.setEnabled(reste > 0)

    def enregistrer_paiement(self):
        montant = self.input_montant.value()
        methode = self.input_methode.currentText()

        if montant <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0")
            return

        PaiementController.enregistrer_paiement(self.facture["id"], montant, methode)

        # Mise à jour du statut de la facture
        paiements = PaiementController.get_paiements_par_facture(self.facture["id"])
        total_paye = sum(p["montant"] for p in paiements)
        if total_paye >= self.facture["montant_total"]:
            FactureController.update_statut_paiement(self.facture["id"], "payé")
        elif total_paye > 0:
            FactureController.update_statut_paiement(self.facture["id"], "partiellement payé")
        else:
            FactureController.update_statut_paiement(self.facture["id"], "non payé")

        QMessageBox.information(self, "Succès", "Paiement enregistré.")
        self.refresh_paiements(paiements)
