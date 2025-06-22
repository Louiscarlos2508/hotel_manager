from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from controllers.reservation_controller import ReservationController


class ArrivalsPage(QWidget):
    def __init__(self, reservation_controller: ReservationController):
        super().__init__()
        self.reservation_controller = reservation_controller
        self.init_ui()
        self.charger_arrivees()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("Arrivées du jour")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        layout.addWidget(title)

        # Recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom ou téléphone...")
        btn_search = QPushButton("Rechercher")
        btn_search.clicked.connect(self.rechercher)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        # Tableau
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Client", "Chambre", "Du", "Au", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def charger_arrivees(self):
        self.table.setRowCount(0)
        try:
            response = self.reservation_controller.list_reservations()
            if not response.get("success", False):
                QMessageBox.warning(self, "Erreur", response.get("error", "Erreur inconnue"))
                return

            reservations = response.get("data", [])

            for r in reservations:
                if r["statut"] not in ["réservée"]:
                    continue  # On ne montre que les check-in possibles

                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(r["client_nom"]))
                self.table.setItem(row, 2, QTableWidgetItem(r["chambre_numero"]))
                self.table.setItem(row, 3, QTableWidgetItem(r["date_arrivee"]))
                self.table.setItem(row, 4, QTableWidgetItem(r["date_depart"]))

                btn_checkin = QPushButton("Check-in")
                btn_checkin.clicked.connect(lambda _, rid=r["id"]: self.confirmer_checkin(rid))
                self.table.setCellWidget(row, 5, btn_checkin)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {e}")


    def confirmer_checkin(self, reservation_id):
        reponse = QMessageBox.question(
            self, "Confirmation",
            "Effectuer le check-in pour cette réservation ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reponse == QMessageBox.Yes:
            result = self.reservation_controller.checkin_reservation(reservation_id)
            if result["success"]:
                QMessageBox.information(self, "Succès", result["message"])
                self.charger_arrivees()
            else:
                QMessageBox.warning(self, "Erreur", result.get("error", "Échec du check-in"))

    def rechercher(self):
        terme = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            nom_item = self.table.item(row, 1)
            chambre_item = self.table.item(row, 2)

            id_text = id_item.text().lower() if id_item else ""
            nom_text = nom_item.text().lower() if nom_item else ""
            chambre_text = chambre_item.text().lower() if chambre_item else ""

            visible = terme in id_text or terme in nom_text or terme in chambre_text
            self.table.setRowHidden(row, not visible)
