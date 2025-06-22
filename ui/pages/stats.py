import matplotlib.pyplot as plt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QFrame, QScrollArea, QGraphicsDropShadowEffect
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt

from controllers.statistiques_controller import StatistiquesController


class StatsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #f4f7fc;
            }
            QLabel {
                color: #2c3e70;
            }
        """)

        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(30)

        # Titre principal
        title = QLabel("📊 Tableau de bord - Statistiques")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        layout.addWidget(title)

        # Cartes Occupation
        layout.addLayout(self._build_occupation_cards())

        # Graphiques
        layout.addWidget(self._build_section("📈 Réservations par Mois", self._create_bar_chart_reservations()))
        layout.addWidget(self._build_section("💰 Revenus mensuels (FCFA)", self._create_bar_chart_revenus()))

        # Tableaux
        layout.addWidget(self._build_section("🏆 Types de chambres les plus réservés", self._build_top_chambres_table()))
        layout.addWidget(self._build_section("👥 Clients les plus fidèles", self._build_top_clients_table()))

        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _build_section(self, title, widget):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #d0dce9;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(container)
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(label)
        layout.addWidget(widget)
        return container

    def _build_occupation_cards(self):
        stats = StatistiquesController.get_occupations_chambres()
        layout = QHBoxLayout()
        layout.setSpacing(30)

        cards = [
            ("🟢 Chambres libres", stats.get("libre", 0), "#2ecc71"),
            ("🔴 Chambres occupées", stats.get("occupée", 0), "#e74c3c")
        ]

        for title, value, color in cards:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 16px;
                    padding: 25px;
                }}
                QLabel {{
                    color: white;
                }}
            """)
            self.apply_shadow(card)

            vbox = QVBoxLayout(card)
            label = QLabel(title)
            label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            count = QLabel(str(value))
            count.setFont(QFont("Segoe UI", 36, QFont.Black))
            vbox.addWidget(label)
            vbox.addWidget(count)
            layout.addWidget(card)

        return layout

    def _create_bar_chart_reservations(self):
        data = StatistiquesController.get_nombre_reservations_par_mois(2024)
        return self._create_bar_chart(data, "Nombre de réservations", "#2980b9")

    def _create_bar_chart_revenus(self):
        data = StatistiquesController.get_revenu_total_par_mois(2024)
        # Convertit les revenus en FCFA
        fcfa_data = {mois: montant for mois, montant in data.items()}
        return self._create_bar_chart(fcfa_data, "Revenus (FCFA)", "#f39c12", money=True)

    def _create_bar_chart(self, data_dict, ylabel, color, money=False):
        fig, ax = plt.subplots(figsize=(10, 6))  # + grand espace
        mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        valeurs = [data_dict.get(i + 1, 0) for i in range(12)]

        bars = ax.bar(mois, valeurs, color=color, edgecolor='black', linewidth=0.5)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title("", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        for bar, val in zip(bars, valeurs):
            text = f"{int(val):,} FCFA" if money else f"{val}"
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 5,
                        text, ha='center', va='top', fontsize=7, color="white")

        fig.patch.set_facecolor('#ffffff')
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        canvas.setMinimumSize(900, 400)
        return canvas

    def _build_top_chambres_table(self):
        top = StatistiquesController.get_top_types_chambres()
        table = QTableWidget(len(top), 3)
        table.setHorizontalHeaderLabels(["ID", "Type de chambre", "Nb Réservations"])
        for i, item in enumerate(top):
            table.setItem(i, 0, QTableWidgetItem(str(item["id"])))
            table.setItem(i, 1, QTableWidgetItem(item["nom"]))
            table.setItem(i, 2, QTableWidgetItem(str(item["nb_reservations"])))
        return self._style_table(table)

    def _build_top_clients_table(self):
        top = StatistiquesController.get_clients_frequents()
        table = QTableWidget(len(top), 4)
        table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Nb Réservations"])
        for i, item in enumerate(top):
            table.setItem(i, 0, QTableWidgetItem(str(item["id"])))
            table.setItem(i, 1, QTableWidgetItem(item["nom"]))
            table.setItem(i, 2, QTableWidgetItem(item["prenom"]))
            table.setItem(i, 3, QTableWidgetItem(str(item["nb_reservations"])))
        return self._style_table(table)

    def _style_table(self, table):
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ccd6e6;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #e6eef6;
                font-weight: bold;
                padding: 8px;
            }
        """)
        table.setFont(QFont("Segoe UI", 10))
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setMinimumHeight(220)
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        table.setStyleSheet(table.styleSheet() + """
            QTableWidget::item {
                color: #2c3e70;
            }
        """)

        return table

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(Qt.black)
        widget.setGraphicsEffect(shadow)

