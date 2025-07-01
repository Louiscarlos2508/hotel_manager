# /home/soutonnoma/PycharmProjects/HotelManger/ui/pages/departures.py

import os
from datetime import date, datetime

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
# --- MODIFICATION : Suppression des imports devenus inutiles ---
# from controllers.chambre_controller import ChambreController
# from controllers.commande_item_controller import CommandeItemController
# from controllers.hotel_info_controller import HotelInfoController

# On garde les contrôleurs réellement utilisés
from controllers.facture_controller import FactureController
from controllers.paiement_controller import PaiementController
from controllers.reservation_controller import ReservationController
from utils.pdf_generator import creer_facture_pdf


class DeparturesPage(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        # On n'a besoin que de ce contrôleur ici
        self.reservation_controller = ReservationController()
        self.init_ui()
        self.charger_departures()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Départs du jour")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par client ou chambre...")
        self.search_input.textChanged.connect(self.rechercher)

        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.charger_departures)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_refresh)
        layout.addLayout(search_layout)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID Résa", "Client", "Chambre", "Arrivée", "Départ Prévu", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def charger_departures(self):
        self.table.setRowCount(0)
        try:
            today_str = date.today().strftime("%Y-%m-%d")
            filtre = {"statuts": ["check-in"], "date_depart": today_str}
            resp = self.reservation_controller.list_reservations(filtre=filtre)

            if not resp.get("success", False):
                QMessageBox.warning(self, "Erreur", resp.get("error", "Erreur inconnue"))
                return

            reservations = resp.get("data", [])
            for row, r in enumerate(reservations):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(f"RES-{r.get('id', '')}"))
                self.table.setItem(row, 1, QTableWidgetItem(r.get("client", "N/A")))
                self.table.setItem(row, 2, QTableWidgetItem(r.get("chambre", "?")))
                self.table.setItem(row, 3, QTableWidgetItem(r.get("date_arrivee", "")))
                self.table.setItem(row, 4, QTableWidgetItem(r.get("date_depart", "")))

                btn_checkout = QPushButton("Check-out")
                btn_checkout.clicked.connect(lambda _, rid=r["id"]: self.afficher_details_checkout(rid))

                btn_payer = QPushButton("Paiement")
                btn_payer.clicked.connect(lambda _, rid=r["id"]: self.ouvrir_page_paiement(rid))

                hbox = QHBoxLayout()
                hbox.setContentsMargins(0, 0, 0, 0)
                hbox.addWidget(btn_checkout)
                hbox.addWidget(btn_payer)

                cell_widget = QWidget()
                cell_widget.setLayout(hbox)
                self.table.setCellWidget(row, 5, cell_widget)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement échoué : {e}")

    # --- SUPPRESSION : La méthode _calculer_totaux est redondante et incorrecte. On la supprime. ---
    # def _calculer_totaux(self, reservation_id):
    #     ...

    def afficher_details_checkout(self, reservation_id):
        try:
            # --- MODIFICATION : On appelle le contrôleur de facture qui est la SEULE source de vérité ---
            calc_resp = FactureController.generer_et_mettre_a_jour_facture(reservation_id)
            if not calc_resp.get("success"):
                raise ValueError(calc_resp.get("error", "Erreur lors du calcul de la facture."))

            # On récupère le dictionnaire de détails complet
            details = calc_resp.get("data", {})

            # On récupère la facture pour connaître le montant déjà payé
            resp_facture = FactureController.get_facture_par_reservation(reservation_id)
            if not resp_facture.get("success"):
                raise ValueError(resp_facture.get("error", "Facture introuvable."))

            facture = resp_facture.get("data")
            if not facture:
                QMessageBox.information(self, "Action requise",
                                        "Aucun paiement n'a encore été effectué pour cette réservation.\n\n"
                                        "Veuillez utiliser le bouton 'Paiement' pour commencer.")
                return

            total_paye = facture.get("montant_paye", 0)
            reste = details.get("total_ttc", 0) - total_paye

            dialog = QDialog(self)
            dialog.setWindowTitle("Validation Check-out")
            layout = QVBoxLayout(dialog)

            # --- MODIFICATION : L'affichage utilise maintenant les détails fournis par le contrôleur ---
            label_info = QLabel(
                f"<b>Hébergement (HT) :</b> {details.get('montant_nuitee_ht', 0):,.0f} FCFA<br>"
                f"<b>TVA Hébergement ({details.get('tva_hebergement_rate', 0):.0%}) :</b> {details.get('tva_hebergement', 0):,.0f} FCFA<br>"
                f"<hr>"
                f"<b>Consommations (HT) :</b> {details.get('montant_consommation_ht', 0):,.0f} FCFA<br>"
                f"<b>TVA Restauration ({details.get('tva_restauration_rate', 0):.0%}) :</b> {details.get('tva_restauration', 0):,.0f} FCFA<br>"
                f"<hr>"
                # --- AJOUT : Affichage des services ---
                f"<b>Services (HT) :</b> {details.get('montant_services_ht', 0):,.0f} FCFA<br>"
                f"<b>TVA Services :</b> {details.get('tva_services', 0):,.0f} FCFA<br>"
                f"<hr>"
                f"<b>Taxe de Séjour (TDT) :</b> {details.get('montant_tdt', 0):,.0f} FCFA<br>"
                f"<hr>"
                f"<b>SOUS-TOTAL (HT) :</b> {details.get('total_ht', 0):,.0f} FCFA<br>"
                f"<b>TOTAL TAXES (TVA+TDT) :</b> {details.get('total_tva', 0) + details.get('montant_tdt', 0):,.0f} FCFA<br>"
                f"<h3>TOTAL À PAYER (TTC) : {details.get('total_ttc', 0):,.0f} FCFA</h3><br>"
                f"<b>Montant déjà payé :</b> {total_paye:,.0f} FCFA<br>"
                f"<b>Reste à payer :</b> <span style='color: red; font-weight: bold;'>{reste:,.0f} FCFA</span>"
            )
            layout.addWidget(label_info)

            button_layout = QHBoxLayout()
            btn_annuler = QPushButton("Annuler")
            btn_annuler.clicked.connect(dialog.reject)

            btn_confirmer = QPushButton("Confirmer le Check-out")
            btn_confirmer.setEnabled(reste <= 0.01)  # Tolérance pour les erreurs de virgule flottante
            btn_confirmer.clicked.connect(lambda: (
                dialog.accept(),
                self.confirmer_checkout(reservation_id)
            ))

            button_layout.addWidget(btn_annuler)
            button_layout.addStretch()
            button_layout.addWidget(btn_confirmer)

            layout.addLayout(button_layout)
            dialog.exec()

        except (Exception, ValueError) as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la vérification du paiement : {e}")

    def confirmer_checkout(self, reservation_id):
        try:
            # L'appel est déjà correct et simplifié
            result = self.reservation_controller.checkout(
                reservation_id=reservation_id,
                user_id=self.user_id
            )

            if result.get("success"):
                self.generer_facture_pdf(reservation_id)
                QMessageBox.information(self, "Succès", "Check-out réussi.")
                self.charger_departures()
            else:
                QMessageBox.warning(self, "Erreur", result.get("error", "Échec du check-out."))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du check-out : {e}")

    def ouvrir_page_paiement(self, reservation_id):
        from ui.pages.paiement_page import PaiementPage
        dialog = QDialog(self)
        dialog.setWindowTitle("Paiement Client")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(600)

        page = PaiementPage(reservation_id)
        layout = QVBoxLayout(dialog)
        layout.addWidget(page)

        dialog.setLayout(layout)
        dialog.exec()
        # On rafraîchit au cas où un paiement a été fait
        self.charger_departures()

    def generer_facture_pdf(self, reservation_id):
        """
        Appelle le générateur de PDF centralisé.
        Celui-ci lira les 'facture_items' qui incluent maintenant les services.
        """
        try:
            result = creer_facture_pdf(reservation_id)
            if result.get("success"):
                QMessageBox.information(self, "Facture Générée",
                                        f"La facture a été enregistrée avec succès :\n{result.get('path')}")
            else:
                QMessageBox.critical(self, "Erreur de Facturation", result.get("error"))
        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", f"Impossible de générer la facture PDF : {e}")

    def rechercher(self):
        terme = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            client = self.table.item(row, 1).text().lower()
            chambre = self.table.item(row, 2).text().lower()
            visible = terme in client or terme in chambre
            self.table.setRowHidden(row, not visible)
