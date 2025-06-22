import os
from datetime import date, datetime

from PySide6.QtGui import QFont, QTextDocument
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog, QDialog
)

from controllers.consommation_controller import ConsommationController
from controllers.facture_controller import FactureController
from controllers.hotel_info_controller import HotelInfoController
from controllers.paiement_controller import PaiementController
from controllers.reservation_controller import ReservationController
from ui.pages.paiement_page import PaiementPage


class DeparturesPage(QWidget):
    def __init__(self, reservation_controller: ReservationController):
        super().__init__()
        self.reservation_controller = reservation_controller
        self.init_ui()
        self.charger_departures()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("Départs du jour")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        layout.addWidget(title)

        # Barre de recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par client ou chambre...")
        btn_search = QPushButton("Rechercher")
        btn_search.clicked.connect(self.rechercher)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        # Tableau
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Client", "Chambre", "Arrivée", "Départ", "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def charger_departures(self):
        self.table.setRowCount(0)
        try:
            today_str = date.today().strftime("%Y-%m-%d")
            response = self.reservation_controller.list_reservations()

            if not response.get("success", False):
                QMessageBox.warning(self, "Erreur", response.get("error", "Erreur inconnue"))
                return

            reservations = response.get("data", [])

            # DEBUG
            print("Statuts reçus :", {r["statut"] for r in reservations})

            for r in reservations:
                print(f"ID: {r.get('id')} statut: '{r.get('statut')}' date_depart: '{r.get('date_depart')}'")

                statut = r.get("statut", "").strip().lower()
                if statut != "en cours":
                    print(f"Ignore pour statut: {r.get('statut')}")
                    continue

                #date_depart_str = r.get("date_depart", "")
                #try:
                #    date_depart_date = datetime.fromisoformat(date_depart_str).date()
                #except Exception:
                #    print(f"Format date incorrect: {date_depart_str}")
                #    continue

                #if date_depart_date != date.today():
                #    print(f"Ignore pour date_depart différente : {date_depart_date}")
                #    continue

                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r.get("id", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(r.get("client_nom", "")))
                self.table.setItem(row, 2, QTableWidgetItem(r.get("chambre_numero", "")))
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

    def ouvrir_page_paiement(self, reservation_id):
        from ui.pages.paiement_page import PaiementPage  # si elle est dans ui/pages

        dialog = QDialog(self)
        dialog.setWindowTitle("Paiement Client")
        dialog.setMinimumWidth(400)

        page = PaiementPage(reservation_id)
        layout = QVBoxLayout(dialog)
        layout.addWidget(page)

        dialog.setLayout(layout)
        dialog.exec()

    def afficher_dialog_paiement(self, reservation_id):
        try:
            facture = FactureController.get_facture_by_reservation(reservation_id)
            if not facture:
                QMessageBox.warning(self, "Erreur", "Aucune facture trouvée pour cette réservation.")
                return

            montant, ok = QInputDialog.getDouble(self, "Montant", "Montant à encaisser :", 0, 0, 999999, 2)
            if not ok or montant <= 0:
                return

            methode, ok = QInputDialog.getItem(
                self, "Méthode de paiement", "Choisissez la méthode de paiement :",
                ["Espèces", "Carte", "Mobile Money", "Autre"], 0, False
            )
            if not ok:
                return

            PaiementController.enregistrer_paiement(facture["id"], montant, methode)

            # Mettre à jour le statut de paiement
            paiements = PaiementController.get_paiements_par_facture(facture["id"])
            total_paye = sum(p['montant'] for p in paiements)

            if total_paye >= facture["montant_total"]:
                FactureController.update_statut_paiement(facture["id"], "payé")
            elif total_paye > 0:
                FactureController.update_statut_paiement(facture["id"], "partiellement payé")
            else:
                FactureController.update_statut_paiement(facture["id"], "non payé")

            QMessageBox.information(self, "Paiement enregistré", "Le paiement a été enregistré avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {e}")

    def afficher_details_checkout(self, reservation_id):
        try:
            facture = FactureController.get_facture_by_reservation(reservation_id)
            if not facture:
                QMessageBox.warning(self, "Erreur", "Aucune facture trouvée.")
                return

            paiements = PaiementController.get_paiements_par_facture(facture["id"])
            total_paye = sum(p['montant'] for p in paiements)
            total_du = facture["montant_total"]
            reste = total_du - total_paye

            dialog = QDialog(self)
            dialog.setWindowTitle("Validation Check-out")
            layout = QVBoxLayout(dialog)

            label_info = QLabel(
                f"<b>Montant total :</b> {total_du} FCFA<br>"
                f"<b>Montant payé :</b> {total_paye} FCFA<br>"
                f"<b>Reste à payer :</b> {reste} FCFA"
            )
            layout.addWidget(label_info)

            button_layout = QHBoxLayout()

            btn_annuler = QPushButton("Annuler")
            btn_annuler.clicked.connect(dialog.reject)

            btn_confirmer = QPushButton("Confirmer le Check-out")
            btn_confirmer.setEnabled(reste <= 0)
            btn_confirmer.clicked.connect(lambda: (
                dialog.accept(),
                self.confirmer_checkout(reservation_id)
            ))

            button_layout.addWidget(btn_annuler)
            button_layout.addStretch()
            button_layout.addWidget(btn_confirmer)

            layout.addLayout(button_layout)
            dialog.setLayout(layout)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la vérification du paiement : {e}")

    def confirmer_checkout(self, reservation_id, montant_consommation=0.0):
        facture = FactureController.get_facture_by_reservation(reservation_id)
        if not facture:
            QMessageBox.warning(self, "Erreur", "Aucune facture trouvée.")
            return

        paiements = PaiementController.get_paiements_par_facture(facture["id"])
        total_paye = sum(p['montant'] for p in paiements)

        if total_paye < facture["montant_total"]:
            QMessageBox.warning(self, "Paiement insuffisant",
                                f"Le client doit encore {facture['montant_total'] - total_paye} FCFA.")
            return

        methode_paiement = facture.get("methode_paiement", "Espèces")

        result = self.reservation_controller.checkout_reservation(
            reservation_id, methode_paiement, montant_consommation
        )
        if result["success"]:
            self.generer_facture_pdf(reservation_id)
            QMessageBox.information(self, "Succès", result["message"])
            self.charger_departures()
        else:
            QMessageBox.warning(self, "Erreur", result.get("error", "Échec du check-out"))

    def generer_facture_pdf(self, reservation_id):
        try:
            facture = FactureController.get_facture_by_reservation(reservation_id)
            if not facture:
                QMessageBox.warning(self, "Erreur", "Facture introuvable.")
                return

            hotel_info_resp = HotelInfoController.get_info()
            if hotel_info_resp["success"]:
                hotel = hotel_info_resp["data"]
                nom = hotel.get("nom", "Nom Hôtel")
                adresse = hotel.get("adresse", "")
                telephone = hotel.get("telephone", "")
                email = hotel.get("email", "")
            else:
                nom, adresse, telephone, email = "Hôtel", "", "", ""

            html = f"""
            <h2 style="text-align:center;">FACTURE - {nom}</h2>
            <p style="text-align:center;">{adresse} | Tél : {telephone} | {email}</p>
            <hr>
            <p><b>Réservation :</b> #{facture['reservation_id']}</p>
            <p><b>Nuitées :</b> {facture['montant_nuitee']} FCFA</p>
            <p><b>Consommations :</b> {facture['montant_consommation']} FCFA</p>
            <p><b>Total :</b> <b>{facture['montant_total']} FCFA</b></p>
            <p><b>Payé par :</b> {facture['methode_paiement']}</p>
            <p style="text-align:center;"><i>Merci pour votre séjour !</i></p>
            """

            # Enregistrer sur bureau dans dossier "Factures"
            bureau = os.path.join(os.path.expanduser("~"), "Desktop")
            dossier = os.path.join(bureau, "Factures")
            os.makedirs(dossier, exist_ok=True)

            fichier_pdf = os.path.join(dossier, f"facture_{facture['id']}.pdf")

            doc = QTextDocument()
            doc.setHtml(html)

            printer = QPrinter()
            printer.setOutputFileName(fichier_pdf)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)

            doc.print(printer)

            QMessageBox.information(self, "Facture", f"Facture enregistrée dans {fichier_pdf}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur génération facture : {e}")

    def rechercher(self):
        terme = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            client = self.table.item(row, 1).text().lower()
            chambre = self.table.item(row, 2).text().lower()
            visible = terme in client or terme in chambre
            self.table.setRowHidden(row, not visible)
