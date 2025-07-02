# /home/soutonnoma/PycharmProjects/HotelManager/ui/login.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controllers.auth_controller import login_user
from ui.home import HomeWindow
# --- AMÉLIORATION : On importe la fonction de centrage centralisée ---
from ui.center_utils import center_on_screen


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.home_window = None  # Garder une référence à la fenêtre principale
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(420, 400)
        self.setStyleSheet("background-color: #002855; color: white;")
        self.old_pos = None

        self.init_ui()
        # Le centrage est maintenant géré par main.py, plus besoin de QTimer ici.

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_widget.setLayout(main_layout)

        # Barre supérieure (inchangée)
        top_bar = self._create_top_bar()

        # Zone de contenu
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignCenter)

        label_title = QLabel("Connexion à l'Espace Hôtel")
        label_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        label_title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Nom d'utilisateur")
        self.username.setStyleSheet(self.input_style())
        self.username.setFixedHeight(40)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(self.input_style())
        self.password.setFixedHeight(40)

        login_btn = QPushButton("Se connecter")
        login_btn.setFixedHeight(40)
        login_btn.setStyleSheet(self.button_style())

        # --- AMÉLIORATION : Connexion via la touche "Entrée" ---
        self.username.returnPressed.connect(login_btn.click)
        self.password.returnPressed.connect(login_btn.click)
        login_btn.clicked.connect(self.handle_login)

        content_layout.addWidget(label_title)
        content_layout.addWidget(self.username)
        content_layout.addWidget(self.password)
        content_layout.addWidget(login_btn)
        content.setLayout(content_layout)

        main_layout.addWidget(top_bar)
        main_layout.addWidget(content)
        self.setCentralWidget(main_widget)

    def handle_login(self):
        """Gère la tentative de connexion."""
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            user_info = login_user(user, pwd)
            if user_info:
                self._on_login_success(user_info)
            else:
                QMessageBox.warning(self, "Erreur", "Identifiants invalides ou compte inactif.")
        except Exception as e:
            # --- AMÉLIORATION : Gestion des erreurs inattendues ---
            QMessageBox.critical(self, "Erreur Critique", f"Une erreur de connexion est survenue : {e}")

    def _on_login_success(self, user_info: dict):
        """Gère la transition vers la fenêtre principale après une connexion réussie."""
        QMessageBox.information(self, "Succès", f"Bienvenue {user_info['nom_complet']}")

        self.home_window = HomeWindow(username=user_info['username'], role=user_info['role'])
        self.home_window.logout_signal.connect(self.show_again_on_logout)

        # --- CORRECTION : On affiche PUIS on centre la fenêtre principale ---
        self.home_window.show()
        center_on_screen(self.home_window)

        self.hide()

    def show_again_on_logout(self):
        """Réaffiche la fenêtre de connexion après une déconnexion."""
        self.username.clear()
        self.password.clear()
        self.show()
        center_on_screen(self) # On recentre au cas où la résolution aurait changé

    def _create_top_bar(self):
        """Crée la barre de titre personnalisée."""
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: #001f3f;")
        top_bar.setFixedHeight(40)
        bar_layout = QHBoxLayout()
        bar_layout.setContentsMargins(10, 0, 10, 0)

        title = QLabel("Connexion - PALM BEACH Hôtel")
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet("color: white;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton { color: white; background-color: transparent; border: none; font-size: 14px; }
            QPushButton:hover { background-color: #ff3b3b; border-radius: 15px; }
        """)
        close_btn.clicked.connect(self.close)

        bar_layout.addWidget(title)
        bar_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        bar_layout.addWidget(close_btn)
        top_bar.setLayout(bar_layout)
        return top_bar

    def input_style(self):
        return """
        QLineEdit {
            border: 2px solid #00b4db; border-radius: 8px; padding-left: 10px;
            background-color: #f0f0f0; color: black;
        }
        QLineEdit:focus { border: 2px solid #0083b0; background-color: white; }
        """

    def button_style(self):
        return """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b4db, stop:1 #0083b0);
            color: white; border: none; border-radius: 8px; font-weight: bold;
        }
        QPushButton:hover { background-color: #0077a6; }
        QPushButton:pressed { background-color: #005f87; }
        """

    # --- Déplacement de la fenêtre (inchangé) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    # --- SUPPRESSION : La méthode est maintenant dans ui/center_utils.py ---
    # def center_on_screen(self):
    #     ...