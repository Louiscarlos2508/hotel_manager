from datetime import date, timedelta
from typing import Dict, Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame

# Assurez-vous que tous les contrôleurs nécessaires sont importés
from controllers.chambre_controller import ChambreController
from controllers.commande_controller import CommandeController
from controllers.commande_item_controller import CommandeItemController
from controllers.paiement_controller import PaiementController
from controllers.probleme_controller import ProblemeController
from controllers.reservation_controller import ReservationController

# --- CONSTANTES pour la clarté et la maintenance ---
ROLE_ADMIN = "admin"
ROLE_RECEPTION = "reception"
ROLE_MANAGER = "bar"


class DashboardPage(QWidget):
    def __init__(self, username: str = None, role: str = None):
        super().__init__()
        self.username = username
        self.role = role

        self.dashboard_builders = {
            ROLE_ADMIN: self._create_admin_dashboard,
            ROLE_RECEPTION: self._create_reception_dashboard,
            ROLE_MANAGER: self._create_manager_bar_dashboard,
        }

        self._setup_ui()
        self.refresh_dashboard()

    def _setup_ui(self):
        """Configure les éléments statiques de l'interface."""
        self.setStyleSheet("background-color: #f0f2f5;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"\U0001F44B Bienvenue {self.username or ''}")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e70;")

        self.main_layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separator)

        # Le layout qui contiendra les cartes
        self.dashboard_content_layout = QHBoxLayout()
        self.dashboard_content_layout.setSpacing(20)
        self.dashboard_content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.dashboard_content_layout)

        self.main_layout.addStretch()

    def refresh_dashboard(self):
        """Rafraîchit toutes les données et l'affichage."""
        while self.dashboard_content_layout.count():
            child = self.dashboard_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        builder_function = self.dashboard_builders.get(self.role)

        if builder_function:
            builder_function()
        else:
            card = self._create_card("Accès restreint", "Votre rôle n'a pas de tableau de bord défini.", "#7f8c8d",
                                     "\U0001F6AB")
            self.dashboard_content_layout.addWidget(card)

    # --- Méthodes de construction des Dashboards ---

    def _create_admin_dashboard(self) -> None:
        metrics = self._prepare_admin_data()
        self.dashboard_content_layout.addWidget(
            self._create_card("Revenu du Jour (FCFA)", f"{metrics['revenue_today']:,.0f}", "#1abc9c", "\U0001F4B5"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Taux d'Occupation", f"{metrics['occupancy_rate']:.1f}%", "#3498db", "\U0001F3E8"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Problèmes en Attente", metrics['unresolved_problems'], "#e74c3c", "\U000026A0"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Revenu Total (FCFA)", f"{metrics['total_revenue']:,.0f}", "#9b59b6", "\U0001F4B0"))

    def _create_reception_dashboard(self) -> None:
        metrics = self._prepare_reception_data()
        self.dashboard_content_layout.addWidget(
            self._create_card("Arrivées Prévues", metrics['arrivals_today'], "#3498db", "\U0001F9F3"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Départs Prévus", metrics['departures_today'], "#f39c12", "\U0001F6EB"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Chambres Occupées", metrics['occupied_rooms'], "#c0392b", "\U0001F6CF"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Chambres Disponibles", metrics['available_rooms'], "#27ae60", "\U0001F511"))

    def _create_manager_bar_dashboard(self) -> None:
        metrics = self._prepare_manager_bar_data()
        self.dashboard_content_layout.addWidget(
            self._create_card("Ventes du Jour (FCFA)", f"{metrics['sales_today']:,.0f}", "#8e44ad", "\U0001F378"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Ventes de la Semaine", f"{metrics['sales_week']:,.0f}", "#2980b9", "\U0001F4C5"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Ventes du Mois", f"{metrics['sales_month']:,.0f}", "#16a085", "\U0001F4C6"))
        self.dashboard_content_layout.addWidget(
            self._create_card("Commandes du Jour", metrics['orders_today'], "#d35400", "\U0001F4DD"))

    # --- Méthodes de préparation des données ---

    def _get_data_from_controller(self, controller_method) -> list:
        """Appelle une méthode de contrôleur et retourne les données ou une liste vide."""
        if not callable(controller_method):
            # C'est cette ligne qui génère votre message d'erreur
            print(f"Erreur: {controller_method} n'est pas une fonction.")
            return []

        response = controller_method()
        if response and response.get("success"):
            return response.get("data", [])
        return []

    def _prepare_admin_data(self) -> Dict[str, Any]:
        today = date.today()

        # VÉRIFICATION DE TOUS LES APPELS : ils doivent être sans parenthèses ()
        paiements = self._get_data_from_controller(PaiementController.get_all)
        reservations = self._get_data_from_controller(ReservationController.list_reservations)
        problemes = self._get_data_from_controller(ProblemeController.liste_problemes)
        chambres = self._get_data_from_controller(ChambreController.get_all_chambres)

        total_rooms = len(chambres)

        revenue_today = sum(p.get('montant', 0) for p in paiements if self._is_today(p.get('date_paiement'), today))
        total_revenue = sum(p.get('montant', 0) for p in paiements)

        occupied_rooms = sum(1 for r in reservations if r.get("statut") == "check-in")
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        unresolved_problems = sum(1 for p in problemes if p.get('statut') not in ['Résolu', 'Annulé'])

        return {
            "revenue_today": revenue_today,
            "total_revenue": total_revenue,
            "occupancy_rate": occupancy_rate,
            "unresolved_problems": unresolved_problems,
        }

    def _prepare_reception_data(self) -> Dict[str, Any]:
        today = date.today()

        # VÉRIFICATION DE TOUS LES APPELS : ils doivent être sans parenthèses ()
        reservations = self._get_data_from_controller(ReservationController.list_reservations)
        chambres = self._get_data_from_controller(ChambreController.get_all_chambres)

        total_rooms = len(chambres)

        arrivals_today = sum(
            1 for r in reservations if self._is_today(r.get('date_arrivee'), today) and r.get('statut') == 'réservée')
        departures_today = sum(
            1 for r in reservations if self._is_today(r.get('date_depart'), today) and r.get('statut') == 'check-in')
        occupied_rooms = sum(1 for r in reservations if r.get("statut") == "check-in")
        available_rooms = total_rooms - occupied_rooms

        return {
            "arrivals_today": arrivals_today, "departures_today": departures_today,
            "occupied_rooms": occupied_rooms, "available_rooms": available_rooms,
        }

    def _prepare_manager_bar_data(self) -> Dict[str, Any]:
        """
        Méthode optimisée qui calcule les ventes et le nombre de commandes
        en se basant sur les articles vendus, pour plus de précision.
        """
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())

        # 1. On utilise notre nouvelle méthode qui fait une seule requête efficace
        items_details = self._get_data_from_controller(CommandeItemController.get_all_with_details)

        sales_today = 0
        sales_week = 0
        sales_month = 0

        # On utilise un "set" pour compter les commandes uniques du jour.
        # Cela résout le bug où des commandes vides étaient comptées.
        orders_today_ids = set()

        # 2. On parcourt la liste unique des articles vendus
        for item in items_details:
            # La date de la commande est déjà incluse, plus besoin de chercher !
            item_date = self._parse_date(item.get('date_commande'))
            if not item_date:
                continue

            price = item.get('quantite', 0) * item.get('prix_unitaire_capture', 0)

            # Calcul des ventes
            if item_date.year == today.year and item_date.month == today.month:
                sales_month += price

            if item_date >= start_of_week:
                sales_week += price

            if item_date == today:
                sales_today += price
                # On ajoute l'ID de la commande au set. Si l'ID est déjà là, rien ne se passe.
                orders_today_ids.add(item.get('commande_id'))

        # 3. Le nombre de commandes du jour est la taille du set.
        orders_today = len(orders_today_ids)

        return {
            "sales_today": sales_today,
            "sales_week": sales_week,
            "sales_month": sales_month,
            "orders_today": orders_today,
        }

    # --- Méthodes utilitaires ---

    def _parse_date(self, date_str: str) -> date | None:
        if not date_str: return None
        try:
            return date.fromisoformat(date_str.split(' ')[0])
        except (ValueError, TypeError):
            return None

    def _is_today(self, date_str: str, today: date) -> bool:
        d = self._parse_date(date_str)
        return d == today if d else False

    def _create_card(self, title: str, value: Any, color: str, icon: str = "") -> QFrame:
        card = QFrame()
        card.setMinimumHeight(120)
        card.setStyleSheet(f"""
            QFrame {{ background-color: {color}; border-radius: 10px; padding: 15px; }}
        """)
        vbox = QVBoxLayout(card)
        title_layout = QHBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_title.setStyleSheet("color: white;")
        lbl_icon = QLabel(icon)
        lbl_icon.setFont(QFont("Segoe UI", 20))
        lbl_icon.setStyleSheet("color: white;")
        lbl_icon.setAlignment(Qt.AlignRight)
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_icon)
        lbl_value = QLabel(str(value))
        lbl_value.setFont(QFont("Segoe UI", 28, QFont.Black))
        lbl_value.setStyleSheet("color: white;")
        vbox.addLayout(title_layout)
        vbox.addWidget(lbl_value)
        vbox.addStretch()
        return card
