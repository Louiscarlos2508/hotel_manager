from datetime import datetime

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from controllers.reservation_controller import ReservationController


class ArrivalsPage(QWidget):
    def __init__(self, reservation_controller: ReservationController):
        super().__init__()
        # Il est préférable de créer une instance du contrôleur ici
        # plutôt que de la passer, pour que la page soit autonome.
        self.reservation_controller = ReservationController()
        self.init_ui()
        self.charger_arrivees()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("Arrivées du jour")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        layout.addWidget(title)

        # Actions
        action_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom, n° chambre...")
        # La recherche se fait en temps réel, le bouton n'est plus nécessaire
        self.search_input.textChanged.connect(self.rechercher)

        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.charger_arrivees)

        action_layout.addWidget(QLabel("🔍"))
        action_layout.addWidget(self.search_input)
        action_layout.addWidget(btn_refresh)
        layout.addLayout(action_layout)

        # Tableau
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID Résa", "Client", "Chambre", "Du", "Au", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def charger_arrivees(self):
        """
        Charge les arrivées du jour et les affiche dans le tableau.
        """
        self.table.setRowCount(0)
        try:
            response = self.reservation_controller.list_reservations()
            if not response.get("success", False):
                QMessageBox.warning(self, "Erreur", response.get("error", "Erreur inconnue"))
                return

            reservations = response.get("data", [])
            today = datetime.now().date()

            arrivals_today = []
            for r in reservations:
                date_arr = datetime.strptime(r["date_arrivee"], "%Y-%m-%d").date()
                if r["statut"] == "réservée" and date_arr == today:
                    arrivals_today.append(r)

            self.table.setRowCount(len(arrivals_today))
            for row, r in enumerate(arrivals_today):
                # --- CORRECTION ICI ---
                # On utilise les clés 'client' et 'chambre' fournies par le modèle.
                self.table.setItem(row, 0, QTableWidgetItem(f"RES-{r['id']}"))
                self.table.setItem(row, 1, QTableWidgetItem(r.get("client", "N/A")))
                self.table.setItem(row, 2, QTableWidgetItem(r.get("chambre", "?")))
                self.table.setItem(row, 3, QTableWidgetItem(r["date_arrivee"]))
                self.table.setItem(row, 4, QTableWidgetItem(r["date_depart"]))

                btn_checkin = QPushButton("✅ Check-in")
                btn_checkin.setToolTip("Enregistrer l'arrivée du client")
                btn_checkin.clicked.connect(lambda _, rid=r["id"]: self.confirmer_checkin(rid))
                self.table.setCellWidget(row, 5, btn_checkin)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {e}")

        # Appliquer la recherche après le chargement
        self.rechercher()

    def confirmer_checkin(self, reservation_id):
        reponse = QMessageBox.question(
            self, "Confirmation",
            f"Effectuer le check-in pour la réservation RES-{reservation_id} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reponse == QMessageBox.Yes:
            # --- CORRECTION ICI ---
            # La méthode dans le contrôleur s'appelle 'checkin'.
            result = self.reservation_controller.checkin(reservation_id)
            if result.get("success"):
                QMessageBox.information(self, "Succès", "Check-in effectué avec succès.")
                self.charger_arrivees()
            else:
                QMessageBox.warning(self, "Erreur", result.get("error", "Échec du check-in"))

    def rechercher(self):
        """
        Filtre les lignes du tableau en fonction du texte de recherche.
        """
        terme = self.search_input.text().lower().strip()
        for row in range(self.table.rowCount()):
            client_item = self.table.item(row, 1)
            chambre_item = self.table.item(row, 2)

            # Vérifie que les items existent avant d'accéder à .text()
            client_text = client_item.text().lower() if client_item else ""
            chambre_text = chambre_item.text().lower() if chambre_item else ""

            # La ligne est visible si le terme est dans le nom du client OU le numéro de chambre
            visible = terme in client_text or terme in chambre_text
            self.table.setRowHidden(row, not visible)
