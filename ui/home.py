# /home/soutonnoma/PycharmProjects/HotelManager/ui/home.py

from datetime import datetime

from PySide6.QtCore import Qt, Signal, QSize, QObject, QThread, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QStackedWidget, QMessageBox, QApplication
)

from controllers.reservation_controller import ReservationController
# Import des contrôleurs et services
from controllers.user_controller import UserController
from services.sync_service import SyncService

# Import des pages de l'UI
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
from ui.pages.users import UsersPage


class SyncWorker(QObject):
    """Worker qui exécute la tâche de synchronisation dans un thread séparé."""
    finished = Signal(dict)

    def __init__(self, sync_service):
        super().__init__()
        self.sync_service = sync_service

    def run(self):
        """Lance la synchronisation et émet un signal quand c'est terminé."""
        result = self.sync_service.synchronize()
        self.finished.emit(result)


class HomeWindow(QMainWindow):
    logout_signal = Signal()

    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.reservation_controller = ReservationController()

        self.user_id = UserController.get_user_by_username(username).get("data", {}).get("id")

        # Dictionnaire pour stocker les pages déjà créées (Lazy Loading)
        self.pages = {}
        self.menu_buttons = {}

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.old_pos = None

        self.setWindowTitle("Accueil - PALM BEACH Hôtel")
        self.resize(1200, 800)
        self.init_ui()
        self.init_sync_service()


    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)

        # --- Menu latéral (inchangé, mais pourrait être refactorisé dans une méthode privée) ---
        self.menu_widget = self._create_menu_widget()
        main_layout.addWidget(self.menu_widget)

        # --- Contenu principal ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0) # Pas de marges pour que le header prenne toute la largeur
        content_layout.setSpacing(0)

        # Header moderne
        top_bar = self._create_header_bar()
        content_layout.addWidget(top_bar)

        # Stack des pages
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        main_layout.addWidget(content_widget)

        # Activer la première page par défaut
        if self.menu_buttons:
            first_btn = list(self.menu_buttons.keys())[0]
            first_btn.setChecked(True)
            self.on_menu_clicked(first_btn) # Utiliser la nouvelle logique pour charger la première page

    def _create_menu_widget(self):
        """Crée et retourne le widget du menu latéral."""
        menu_widget = QWidget()
        menu_widget.setFixedWidth(280)
        menu_widget.setStyleSheet("background-color: #1e2f4a;")
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(30, 30, 30, 30)
        menu_layout.setSpacing(15)

        # Logo et nom de l'hôtel
        logo_img = QLabel()
        pixmap = QPixmap("assets/icons/hotel.png")
        logo_img.setPixmap(pixmap.scaledToWidth(120, Qt.SmoothTransformation))
        logo_img.setAlignment(Qt.AlignCenter)
        logo_text = QLabel("PALM BEACH\nHôtel")
        logo_text.setFont(QFont("Segoe UI", 20, QFont.Bold))
        logo_text.setStyleSheet("color: #a1cdf1;")
        logo_text.setAlignment(Qt.AlignCenter)
        logo_text.setWordWrap(True)
        logo_text.setFixedWidth(220)
        menu_layout.addWidget(logo_img, alignment=Qt.AlignCenter)
        menu_layout.addWidget(logo_text, alignment=Qt.AlignCenter)
        menu_layout.addSpacing(40)

        # Définition des items du menu par rôle
        all_items = {
            "admin": [
                ("Tableau de bord", lambda: DashboardPage(self.username, self.role), "dashboard.png"),
                ("Gestion utilisateurs", lambda: UsersPage(), "users.png"),
                ("Gestion chambres", lambda: RoomsPage(), "rooms.png"),
                ("Clients", lambda: ClientsPage(), "clients.png"),
                ("Services", lambda: ServicesPage(self.role), "services.png"),
                ("Problèmes", lambda: ProblemesPage(), "warning.png"),
                ("Gestion Produits", lambda: ProduitsPage(), "products.png"),
                ("Paramètres", lambda: SettingsPage(), "settings.png"),
            ],
            "reception": [
                ("Tableau de bord", lambda: DashboardPage(self.username, self.role), "dashboard.png"),
                ("Réservations", lambda: ReservationsPage(self.user_id), "reservations.png"),
                ("Arrivées", lambda: ArrivalsPage(self.reservation_controller), "arrivals.png"),
                ("Départs", lambda: DeparturesPage(self.user_id), "departures.png"),
                ("Clients", lambda: ClientsPage(), "clients.png"),
                ("Services", lambda: ServicesPage(self.role), "services.png"),
                ("Problèmes", lambda: ProblemesPage(), "warning.png"),
            ],
            "manager": [ # 'bar' est un alias pour 'manager'
                ("Tableau de bord", lambda: DashboardPage(self.username, self.role), "dashboard.png"),
                ("Consommations clients", lambda: BarPage(self.user_id), "bar.png"),
                ("Restauration", lambda: RestaurationPage(self.user_id), "food.png"),
                ("Gestion Produits", lambda: ProduitsPage(), "products.png"),
            ]
        }
        # 'bar' utilise la même configuration que 'manager'
        all_items["bar"] = all_items["manager"]

        items_for_role = all_items.get(self.role, [("Tableau de bord", lambda: DashboardPage(self.username, self.role), "dashboard.png")])

        # Création des boutons
        for name, page_func, icon_file in items_for_role:
            btn = QPushButton(name.replace("\n", " "))
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background-color: transparent; color: #dbe9f4; padding: 14px 20px; border-radius: 8px; text-align: left; font-size: 17px; font-weight: 600; border: 2px solid transparent; }
                QPushButton:checked { background-color: #3a5c8c; border-left: 6px solid #65b0f1; font-weight: 700; color: white; }
                QPushButton:hover { background-color: #2d466b; }
            """)
            icon_path = f"assets/icons/{icon_file}"
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(lambda _, b=btn: self.on_menu_clicked(b))
            menu_layout.addWidget(btn)
            self.menu_buttons[btn] = (name, page_func)

        menu_layout.addStretch()

        # Bouton déconnexion
        logout_btn = QPushButton("Déconnexion")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton { background-color: #65b0f1; color: white; font-weight: bold; border-radius: 12px; padding: 14px; font-size: 18px; margin-top: 20px; }
            QPushButton:hover { background-color: #4a8ddc; }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        menu_layout.addWidget(logout_btn)

        return menu_widget

    def _create_header_bar(self):
        """Crée et retourne le widget du header."""
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #e0e0e0;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 10, 0)

        # Titre de la page actuelle (sera mis à jour)
        self.header_title = QLabel("Tableau de bord")
        self.header_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.header_title.setStyleSheet("color: #2c3e70;")
        top_layout.addWidget(self.header_title)
        top_layout.addStretch()

        # Infos utilisateur
        user_display = QLabel(f"{self.username} ({self.role})")
        user_display.setStyleSheet("font-size: 14px; color: #555; background-color: #f0f3f8; padding: 6px 16px; border-radius: 14px;")
        top_layout.addWidget(user_display)

        # Contrôles de la fenêtre
        for txt, func in [("—", self.showMinimized), ("□", self.toggle_max_restore), ("✕", self.close)]:
            btn = QPushButton(txt)
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("QPushButton { background-color: transparent; border: none; font-size: 18px; font-weight: bold; color: #444; } QPushButton:hover { background-color: #e8e8e8; border-radius: 6px; }")
            btn.clicked.connect(func)
            top_layout.addWidget(btn)

        return top_bar

    def on_menu_clicked(self, clicked_button):
        """
        Gère le changement de page avec une logique de "Lazy Loading".
        La page n'est créée que lors du premier accès.
        """
        # Désélectionner tous les autres boutons
        for btn in self.menu_buttons:
            if btn != clicked_button:
                btn.setChecked(False)
        clicked_button.setChecked(True)

        name, page_func = self.menu_buttons[clicked_button]

        # Si la page n'a jamais été créée, on la crée
        if name not in self.pages:
            page = page_func()
            self.pages[name] = page
            self.stack.addWidget(page)

        # On affiche la page correspondante
        self.stack.setCurrentWidget(self.pages[name])
        self.header_title.setText(name.replace("\n", " "))

    def init_sync_service(self):
        """Initialise et démarre le service de synchronisation périodique."""
        try:
            self.sync_service = SyncService()
            self.sync_status_label = QLabel("Synchro: Prêt")
            self.statusBar().addPermanentWidget(self.sync_status_label)
            self.run_background_sync()
            self.sync_timer = QTimer(self)
            self.sync_timer.timeout.connect(self.run_background_sync)
            self.sync_timer.start(60000)
        except ValueError as e:
            QMessageBox.critical(self, "Erreur de Configuration", str(e))

    def run_background_sync(self):
        """Lance la synchronisation dans un thread séparé pour ne pas bloquer l'UI."""
        self.sync_status_label.setText("Synchro: En cours...")
        self.thread = QThread()
        self.worker = SyncWorker(self.sync_service)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_sync_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_sync_finished(self, result):
        """Méthode appelée quand la synchronisation est terminée."""
        if result.get("success"):
            self.sync_status_label.setText(f"Synchro: OK ({datetime.now().strftime('%H:%M:%S')})")
        else:
            error_msg = result.get('error', 'Erreur inconnue')
            self.sync_status_label.setText("Synchro: Erreur!")
            self.sync_status_label.setToolTip(error_msg)
            if "timeout" not in error_msg.lower():
                QMessageBox.warning(self, "Erreur de Synchronisation", f"La synchronisation a échoué : {error_msg}")

        # Rafraîchir la vue actuelle pour afficher les nouvelles données
        # CORRECTION : Utilisation de self.stack au lieu de self.stacked_widget
        current_widget = self.stack.currentWidget()
        # On standardise sur la méthode 'refresh_data' pour toutes les pages
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
        # Fallback pour les anciennes méthodes, à unifier plus tard
        elif hasattr(current_widget, 'refresh_table'):
            current_widget.refresh_table()
        elif hasattr(current_widget, 'refresh_dashboard'):
            current_widget.refresh_dashboard()

    def toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def handle_logout(self):
        self.logout_signal.emit()
        self.close()

    # --- Méthodes pour la fenêtre sans cadre ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() < 60: # Drag seulement sur le header
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def closeEvent(self, event):
        # Plus besoin de fermer la connexion DB ici, car elle n'est plus stockée
        event.accept()
