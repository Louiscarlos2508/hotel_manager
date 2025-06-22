from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from datetime import datetime, timedelta

from controllers.statistiques_controller import StatistiquesController
from controllers.consommation_controller import ConsommationController


class DashboardPage(QWidget):
    def __init__(self, username=None, role=None):
        super().__init__()
        self.username = username
        self.role = role
        self.setStyleSheet("QLabel { color: #2c3e70; }")
        layout = QVBoxLayout(self)
        layout.setSpacing(30)

        # Titre
        title = QLabel(f"👋 Bienvenue {username or ''} - {role.capitalize()}")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Rôle spécifique
        if role == "admin":
            layout.addLayout(self._admin_cards())
        elif role == "reception":
            layout.addLayout(self._reception_cards())
        elif role == "bar":
            layout.addLayout(self._bar_cards())
        else:
            layout.addWidget(self._simple_card("Accès restreint", "Rôle non autorisé", "#7f8c8d"))

        layout.addStretch()

    def _card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            background-color: {color};
            border-radius: 14px;
            padding: 25px;
        """)
        vbox = QVBoxLayout(card)
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_title.setStyleSheet("color: white;")
        lbl_value = QLabel(str(value))
        lbl_value.setFont(QFont("Segoe UI", 30, QFont.Black))
        lbl_value.setStyleSheet("color: white;")
        vbox.addWidget(lbl_title)
        vbox.addWidget(lbl_value)
        return card

    def _simple_card(self, title, value, color):
        layout = QHBoxLayout()
        layout.addWidget(self._card(title, value, color))
        return layout

    def _admin_cards(self):
        stats = StatistiquesController.get_occupations_chambres()
        reservations = StatistiquesController.get_nombre_reservations_par_mois(datetime.now().year)
        revenus = StatistiquesController.get_revenu_total_par_mois(datetime.now().year)

        total_res = sum(reservations.values())
        total_revenu = sum(revenus.values())

        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addWidget(self._card("Chambres libres", stats.get("libre", 0), "#2ecc71"))
        layout.addWidget(self._card("Chambres occupées", stats.get("occupée", 0), "#e74c3c"))
        layout.addWidget(self._card("Réservations (année)", total_res, "#2980b9"))
        layout.addWidget(self._card("Revenus (FCFA)", f"{total_revenu:.2f}", "#f39c12"))
        return layout

    def _reception_cards(self):
        stats = StatistiquesController.get_occupations_chambres()
        mois_actuel = datetime.now().month
        reservations = StatistiquesController.get_nombre_reservations_par_mois(datetime.now().year)
        res_mois = reservations.get(mois_actuel, 0)

        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addWidget(self._card("Réservations (ce mois)", res_mois, "#3498db"))
        layout.addWidget(self._card("Chambres libres", stats.get("libre", 0), "#27ae60"))
        layout.addWidget(self._card("Chambres occupées", stats.get("occupée", 0), "#c0392b"))
        return layout

    def _bar_cards(self):
        today = datetime.now().date()
        lundi = today - timedelta(days=today.weekday())

        response = ConsommationController.get_consommations_by_date_range(lundi, today)
        if response.get("success"):
            consommations = response.get("data", [])
        else:
            consommations = []

        total_jour = sum(c['quantite'] * c['prix_unitaire'] for c in consommations if c.get('date') == str(today))
        total_semaine = sum(c['quantite'] * c['prix_unitaire'] for c in consommations)

        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addWidget(self._card("Total du jour (FCFA)", f"{total_jour:.2f}", "#8e44ad"))
        layout.addWidget(self._card("Semaine (FCFA)", f"{total_semaine:.2f}", "#1abc9c"))
        layout.addWidget(self._card("Articles vendus", len(consommations), "#f39c12"))
        return layout

