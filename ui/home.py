from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QStackedWidget
)

from controllers.reservation_controller import ReservationController
from database.db import get_connection
from ui.pages.arrivals import ArrivalsPage
from ui.pages.bar import BarPage
from ui.pages.clients import ClientsPage
from ui.pages.dashboard import DashboardPage
from ui.pages.departures import DeparturesPage
from ui.pages.problemes import ProblemesPage
from ui.pages.produit import ProduitsPage
from ui.pages.reservations import ReservationsPage
from ui.pages.restauration import RestaurationPage
from ui.pages.rooms import RoomsPage
from ui.pages.services import ServicesPage
from ui.pages.settings import SettingsPage
from ui.pages.stats import StatsPage
from ui.pages.users import UsersPage


class HomeWindow(QMainWindow):
    logout_signal = Signal()

    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.pages = {}
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.old_pos = None

        self.db = get_connection()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.old_pos = None

        self.setWindowTitle("Accueil - PALM BEACH Hôtel")
        self.resize(1200, 800)
        self.init_ui()


    def init_ui(self):
        # Main container layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Menu latéral ---
        self.menu_widget = QWidget()
        self.menu_widget.setFixedWidth(280)
        self.menu_widget.setStyleSheet("""
            background-color: #1e2f4a;
        """)
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(30, 30, 30, 30)
        self.menu_layout.setSpacing(15)

        # Logo + hotel name corrigé (2 lignes, largeur limitée)
        logo_img = QLabel()
        pixmap = QPixmap("assets/icons/hotel.png")
        if not pixmap.isNull():
            logo_img.setPixmap(pixmap.scaledToWidth(120, Qt.SmoothTransformation))
        logo_img.setAlignment(Qt.AlignCenter)

        logo_text = QLabel("PALM BEACH\nHôtel")
        logo_text.setFont(QFont("Segoe UI", 20, QFont.Bold))
        logo_text.setStyleSheet("color: #a1cdf1;")
        logo_text.setAlignment(Qt.AlignCenter)
        logo_text.setWordWrap(True)
        logo_text.setFixedWidth(220)  # limite largeur pour forcer retour à la ligne

        self.menu_layout.addWidget(logo_img, alignment=Qt.AlignCenter)
        self.menu_layout.addWidget(logo_text, alignment=Qt.AlignCenter)
        self.menu_layout.addSpacing(40)

        # Menu items en fonction du rôle
        self.menu_buttons = {}
        items = []

        if self.role == "admin":
            items = [
                ("Tableau de bord", lambda: DashboardPage(self.username, self.role), "dashboard.png"),
                ("Gestion \nutilisateurs", lambda: UsersPage(), "users.png"),
                ("Gestion chambres", lambda: RoomsPage(), "rooms.png"),
                ("Clients", lambda: ClientsPage(), "clients.png"),
                ("Services", lambda: ServicesPage(self.role), "services.png"),
                ("Problèmes", lambda: ProblemesPage(), "warning.png"),
                ("Gestion Produits", lambda: ProduitsPage(), "products.png"),
                #("Statistiques", lambda: StatsPage(), "stats.png"),
                ("Paramètres", lambda: SettingsPage(), "settings.png"),
            ]
        elif self.role == "reception":
            items = [
                ("Tableau de bord", lambda: DashboardPage(self.username, self.role), "dashboard.png"),
                ("Réservations", lambda: ReservationsPage(), "reservations.png"),
                ("Arrivées", lambda: ArrivalsPage(ReservationController(self.db)), "arrivals.png"),
                ("Départs", lambda: DeparturesPage(ReservationController(self.db)), "departures.png"),
                ("Clients", lambda: ClientsPage(), "clients.png"),
                ("Services", lambda: ServicesPage(self.role), "services.png"),
                ("Problèmes", lambda: ProblemesPage(), "warning.png"),
            ]
        elif self.role == "manager" or self.role == "bar":
            items = [
                ("Tableau de bord", lambda: DashboardPage(self.username, self.role), "dashboard.png"),
                ("Consommations \n clients", lambda: BarPage(), "bar.png"),
                ("Restauration", lambda: RestaurationPage(), "food.png"),
                ("Gestion Produits", lambda: ProduitsPage(), "products.png"),
            ]
        else:
            items = [("Tableau de bord", lambda: DashboardPage(self.username, self.role), "dashboard.png")]

        # Création des boutons du menu
        for name, page_func, icon_file in items:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #dbe9f4;
                    padding: 14px 20px;
                    border-radius: 8px;
                    text-align: left;
                    font-size: 17px;
                    font-weight: 600;
                    border: 2px solid transparent;
                }
                QPushButton:checked {
                    background-color: #3a5c8c;
                    border-left: 6px solid #65b0f1;
                    font-weight: 700;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #2d466b;
                }
            """)
            icon_path = f"assets/icons/{icon_file}"
            icon_pixmap = QPixmap(icon_path)
            if not icon_pixmap.isNull():
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(24, 24))

            btn.clicked.connect(self.on_menu_clicked)
            self.menu_layout.addWidget(btn)
            self.menu_buttons[btn] = (name, page_func)

        self.menu_layout.addStretch()

        # Bouton déconnexion
        logout_btn = QPushButton("Déconnexion")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #65b0f1;
                color: white;
                font-weight: bold;
                border-radius: 12px;
                padding: 14px;
                font-size: 18px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #4a8ddc;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        self.menu_layout.addWidget(logout_btn)

        # --- Contenu principal ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # --- Header moderne ---
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            background-color: #f0f3f8;
            border-bottom: 1px solid #dcdfe6;
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)
        top_layout.setSpacing(15)

        # Logo miniature à gauche
        icon_left = QLabel()
        icon_left.setPixmap(QPixmap("assets/logo.png").scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(icon_left)

        # Titre centré
        header_title = QLabel("PALM BEACH Hôtel - Interface de gestion")
        header_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_title.setStyleSheet("color: #2c3e70;")
        top_layout.addWidget(header_title)
        top_layout.addStretch()

        # Utilisateur
        user_display = QLabel(f"{self.username}  |  {self.role}")
        user_display.setStyleSheet("""
            font-size: 14px;
            color: #555;
            background-color: #dfe9f5;
            padding: 6px 16px;
            border-radius: 14px;
        """)
        top_layout.addWidget(user_display)

        # Contrôles fenêtre
        for txt, func in [("—", self.showMinimized), ("□", self.toggle_max_restore), ("✕", self.close)]:
            btn = QPushButton(txt)
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 18px;
                    font-weight: bold;
                    color: #444;
                }
                QPushButton:hover {
                    background-color: #e1e9f8;
                    border-radius: 6px;
                }
            """)
            btn.clicked.connect(func)
            top_layout.addWidget(btn)
            content_layout.addWidget(top_bar)

        # Stack des pages
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        # Ajouter pages dans stack
        for btn, (name, page_func) in self.menu_buttons.items():
            page = page_func()
            self.pages[name] = page
            self.stack.addWidget(page)

        main_layout.addWidget(self.menu_widget)
        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)

        # Sélection première page par défaut
        first_btn = list(self.menu_buttons.keys())[0]
        first_btn.setChecked(True)
        self.stack.setCurrentWidget(self.pages[self.menu_buttons[first_btn][0]])

    def toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def on_menu_clicked(self):
        btn = self.sender()
        for b in self.menu_buttons:
            b.setChecked(False)
        btn.setChecked(True)

        name, page_func = self.menu_buttons[btn]

        if name in ["Tableau de bord", "Arrivées", "Départs", "Clients", "Réservations", "Services", "Restauration", "Problèmes", "Consommations \n clients"]:
            # Supprimer l'ancienne page si elle existe
            old_page = self.pages.get(name)
            if old_page:
                self.stack.removeWidget(old_page)
                old_page.deleteLater()

            # Recréer dynamiquement une nouvelle page Dashboard
            new_dashboard = page_func()
            self.pages[name] = new_dashboard
            self.stack.addWidget(new_dashboard)
            self.stack.setCurrentWidget(new_dashboard)
        else:
            self.stack.setCurrentWidget(self.pages[name])

    def handle_logout(self):
        self.logout_signal.emit()
        self.close()

    # Exemple de page Tableau de bord (Admin & Reception)
    def page_dashboard(self):
        return DashboardPage(self.username, self.role)

    # Exemple page Gestion utilisateurs (admin)
    def page_users(self):
        return UsersPage()

    # Exemple page Réservations (admin, reception)
    def page_reservations(self):
        return ReservationsPage()

    # Page Statistiques (admin)
    def page_stats(self):
        return StatsPage()

    def page_settings(self):
        return SettingsPage()

    # Réception - Arrivées
    def page_arrivals(self):
        reservation_controller = ReservationController(self.db)
        return ArrivalsPage(reservation_controller)

    # Réception - Départs
    def page_departures(self):
        reservation_controller = ReservationController(self.db)
        return DeparturesPage(reservation_controller)

    # Réception - Clients
    def page_clients(self):
        return ClientsPage()

    # Bar & Restauration
    def page_bar(self):
        return BarPage()

    # Gestion chambres (admin)
    def page_rooms(self):
        return RoomsPage()

    def page_services(self):
        return ServicesPage()

    def page_problemes(self):
        return ProblemesPage()

    def page_restauration(self):
        return RestaurationPage()

    # --- Drag fenêtre frameless ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def closeEvent(self, event):
        # Fermer proprement la connexion base avant de fermer la fenêtre
        if self.db:
            self.db.close()
        event.accept()