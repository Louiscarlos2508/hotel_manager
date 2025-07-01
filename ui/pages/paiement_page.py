# /home/soutonnoma/PycharmProjects/HotelManger/ui/pages/paiement_page.py

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QFormLayout, QDoubleSpinBox, QComboBox, QPushButton, QMessageBox, QHeaderView, QGroupBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

# On a seulement besoin de ces deux contrôleurs
from controllers.facture_controller import FactureController
from controllers.paiement_controller import PaiementController


class PaiementPage(QWidget):
    def __init__(self, reservation_id):
        super().__init__()
        self.reservation_id = reservation_id
        self.facture = None
        self.init_ui()
        self.load_data_and_refresh_ui()

    def init_ui(self):
        """
        Interface utilisateur révisée pour afficher les détails fiscaux.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # --- Récapitulatif des coûts avec détails HT, TVA, TDT ---
        recap_group = QGroupBox("Récapitulatif de la Facture")
        recap_layout = QFormLayout(recap_group)
        recap_layout.setLabelAlignment(Qt.AlignRight)

        self.label_total_hebergement_ht = QLabel("...")
        self.label_tva_hebergement = QLabel("...")
        self.label_total_consommations_ht = QLabel("...")
        self.label_tva_restauration = QLabel("...")
        # --- AJOUT : Labels pour les services ---
        self.label_total_services_ht = QLabel("...")
        self.label_tva_services = QLabel("...")
        # --- FIN DE L'AJOUT ---
        self.label_tdt = QLabel("...")
        self.label_total_general_ttc = QLabel("...")
        self.label_total_general_ttc.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.label_total_general_ttc.setStyleSheet("color: #2c3e50;")

        recap_layout.addRow("<b>Hébergement (HT):</b>", self.label_total_hebergement_ht)
        recap_layout.addRow("<b>TVA Hébergement:</b>", self.label_tva_hebergement)
        recap_layout.addRow("<b>Consommations (HT):</b>", self.label_total_consommations_ht)
        recap_layout.addRow("<b>TVA Restauration:</b>", self.label_tva_restauration)
        # --- AJOUT : Lignes pour les services dans le formulaire ---
        recap_layout.addRow("<b>Services (HT):</b>", self.label_total_services_ht)
        recap_layout.addRow("<b>TVA Services:</b>", self.label_tva_services)
        # --- FIN DE L'AJOUT ---
        recap_layout.addRow("<b>Taxe de Séjour (TDT):</b>", self.label_tdt)
        recap_layout.addRow("<h3>Montant Total (TTC):</h3>", self.label_total_general_ttc)
        layout.addWidget(recap_group)

        # --- Formulaire de paiement ---
        paiement_group = QGroupBox("Encaisser un Paiement")
        paiement_form = QFormLayout(paiement_group)
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 10_000_000)
        self.input_montant.setSuffix(" FCFA")
        self.input_montant.setDecimals(0)
        self.input_montant.setGroupSeparatorShown(True)
        self.input_methode = QComboBox()
        self.input_methode.addItems(["Espèces", "Carte de crédit", "Mobile Money", "Virement", "Autre"])
        paiement_form.addRow("Montant à encaisser:", self.input_montant)
        paiement_form.addRow("Méthode de paiement:", self.input_methode)
        self.btn_enregistrer = QPushButton("Enregistrer le paiement")
        self.btn_enregistrer.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_enregistrer.clicked.connect(self.enregistrer_paiement)
        paiement_form.addRow(self.btn_enregistrer)
        layout.addWidget(paiement_group)

        # --- Historique et Solde ---
        history_group = QGroupBox("Historique et Solde")
        history_layout = QVBoxLayout(history_group)
        self.table_paiements = QTableWidget()
        self.table_paiements.setColumnCount(3)
        self.table_paiements.setHorizontalHeaderLabels(["Date", "Montant", "Méthode"])
        self.table_paiements.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_paiements.setEditTriggers(QTableWidget.NoEditTriggers)
        history_layout.addWidget(self.table_paiements)

        recap_paiement_layout = QFormLayout()
        recap_paiement_layout.setLabelAlignment(Qt.AlignRight)
        self.label_total = QLabel("...")
        self.label_paye = QLabel("...")
        self.label_reste = QLabel("...")
        self.label_reste.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.label_reste.setStyleSheet("color: #c0392b;")
        recap_paiement_layout.addRow("Montant total facture (TTC):", self.label_total)
        recap_paiement_layout.addRow("Montant déjà payé:", self.label_paye)
        recap_paiement_layout.addRow("Reste à payer:", self.label_reste)
        history_layout.addLayout(recap_paiement_layout)
        layout.addWidget(history_group)

    def load_data_and_refresh_ui(self):
        """
        Charge et calcule toutes les données, et met à jour la facture et l'UI.
        """
        try:
            # 1. Le contrôleur calcule, met à jour la facture ET retourne les détails
            calc_resp = FactureController.generer_et_mettre_a_jour_facture(self.reservation_id)
            if not calc_resp.get("success"):
                raise Exception(calc_resp.get("error", "Erreur lors du calcul de la facture."))

            # On récupère le dictionnaire de détails
            details_facture = calc_resp.get("data", {})

            # 2. On récupère la facture fraîchement mise à jour (pour le montant_paye)
            facture_resp = FactureController.get_facture_par_reservation(self.reservation_id)
            if not facture_resp.get("success") or not facture_resp.get("data"):
                raise Exception("Facture introuvable après la mise à jour.")
            self.facture = facture_resp["data"]

            # 3. On récupère l'historique des paiements
            paiements_resp = PaiementController.get_paiements_par_facture(self.facture["id"])
            if not paiements_resp.get("success"):
                raise Exception(paiements_resp.get("error", "Erreur chargement des paiements."))
            paiements = paiements_resp.get("data", [])

            # 4. On met à jour toute l'interface avec les données fraîches
            self._update_display(details_facture, self.facture, paiements)

        except Exception as e:
            QMessageBox.critical(self, "Erreur de chargement", str(e))
            self.close()

    def _update_display(self, details, facture, paiements):
        """Met à jour tous les widgets de l'UI avec les données fournies."""
        # Mise à jour du récapitulatif détaillé
        self.label_total_hebergement_ht.setText(f"{details.get('montant_nuitee_ht', 0):,.0f} FCFA")
        self.label_tva_hebergement.setText(
            f"{details.get('tva_hebergement', 0):,.0f} FCFA ({details.get('tva_hebergement_rate', 0):.0%})")
        self.label_total_consommations_ht.setText(f"{details.get('montant_consommation_ht', 0):,.0f} FCFA")
        self.label_tva_restauration.setText(
            f"{details.get('tva_restauration', 0):,.0f} FCFA ({details.get('tva_restauration_rate', 0):.0%})")

        # --- AJOUT : Mise à jour des labels de services ---
        self.label_total_services_ht.setText(f"{details.get('montant_services_ht', 0):,.0f} FCFA")
        self.label_tva_services.setText(f"{details.get('tva_services', 0):,.0f} FCFA")
        # --- FIN DE L'AJOUT ---

        self.label_tdt.setText(f"{details.get('montant_tdt', 0):,.0f} FCFA")
        self.label_total_general_ttc.setText(f"{details.get('total_ttc', 0):,.0f} FCFA")

        # Mise à jour de l'historique et du solde
        total_ttc = facture.get('montant_total_ttc', 0)
        total_paye = facture.get('montant_paye', 0)
        reste_a_payer = total_ttc - total_paye

        self.label_total.setText(f"{total_ttc:,.0f} FCFA")
        self.label_paye.setText(f"{total_paye:,.0f} FCFA")
        self.label_reste.setText(f"{reste_a_payer:,.0f} FCFA")

        # Mise à jour de la table des paiements
        self.table_paiements.setRowCount(0)
        for p in paiements:
            row = self.table_paiements.rowCount()
            self.table_paiements.insertRow(row)
            date_paiement = datetime.fromisoformat(p["date_paiement"]).strftime("%d/%m/%Y %H:%M")
            self.table_paiements.setItem(row, 0, QTableWidgetItem(date_paiement))
            self.table_paiements.setItem(row, 1, QTableWidgetItem(f"{p['montant']:,.0f} FCFA"))
            self.table_paiements.setItem(row, 2, QTableWidgetItem(p["methode"]))

        # Mise à jour du formulaire de paiement
        self.input_montant.setValue(reste_a_payer if reste_a_payer > 0 else 0)
        self.btn_enregistrer.setEnabled(reste_a_payer > 0.01)  # Tolérance pour les floats

    def enregistrer_paiement(self):
        """Gère l'action de cliquer sur le bouton pour enregistrer un paiement."""
        montant = self.input_montant.value()
        methode = self.input_methode.currentText()

        if montant <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0.")
            return

        # Le contrôleur de paiement gère la création du paiement ET la mise à jour de la facture
        paiement_resp = PaiementController.creer_paiement(self.facture["id"], montant, methode)
        if not paiement_resp.get("success"):
            QMessageBox.warning(self, "Erreur", paiement_resp.get("error"))
            return

        # Après un paiement réussi, on recharge simplement tout pour garantir la cohérence
        self.load_data_and_refresh_ui()
        QMessageBox.information(self, "Succès", "Paiement enregistré.")
