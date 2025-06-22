from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QGuiApplication
from controllers.auth_controller import login_user
from ui.home import HomeWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(420, 400)
        self.setStyleSheet("background-color: #002855; color: white;")
        self.old_pos = None

        self.init_ui()
        QTimer.singleShot(0, self.center_on_screen)

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_widget.setLayout(main_layout)

        # Barre supérieure
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
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff3b3b;
                border-radius: 15px;
            }
        """)
        close_btn.clicked.connect(self.close)

        bar_layout.addWidget(title)
        bar_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        bar_layout.addWidget(close_btn)
        top_bar.setLayout(bar_layout)

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
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        user_info = login_user(user, pwd)

        if user_info:
            QMessageBox.information(self, "Succès", f"Bienvenue {user_info['nom_complet']}")

            self.home = HomeWindow(username=user_info['username'], role=user_info['role'])
            self.home.logout_signal.connect(self.show_again)
            self.home.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants invalides")

    def show_again(self):
        self.username.clear()
        self.password.clear()
        self.show()

    def input_style(self):
        return """
        QLineEdit {
            border: 2px solid #00b4db;
            border-radius: 8px;
            padding-left: 10px;
            background-color: #f0f0f0;
            color: black;
        }
        QLineEdit:focus {
            border: 2px solid #0083b0;
            background-color: white;
        }
        """

    def button_style(self):
        return """
        QPushButton {
            background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #00b4db, stop:1 #0083b0
            );
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0077a6;
        }
        QPushButton:pressed {
            background-color: #005f87;
        }
        """

    # Déplacement de la fenêtre
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

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        screen_geom = screen.availableGeometry()
        fg = self.frameGeometry()
        fg.moveCenter(screen_geom.center())
        self.move(fg.topLeft())
