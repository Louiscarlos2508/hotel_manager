# /home/soutonnoma/PycharmProjects/HotelManger/main.py

import sys
from PySide6.QtWidgets import QApplication

from database.db import init_db
from ui.login import LoginWindow
from ui.splash import SplashScreen
# --- MODIFICATION : On importe notre nouvelle fonction utilitaire ---
from ui.center_utils import center_on_screen


def show_login():
    """Crée, affiche et ENSUITE centre la fenêtre de connexion."""
    login = LoginWindow()
    login.show()
    center_on_screen(login)  # <-- On centre APRÈS .show()
    app.login_window = login


if __name__ == "__main__":
    init_db()

    app = QApplication(sys.argv)

    splash = SplashScreen(duration=3000, on_finish=show_login)
    splash.show()
    center_on_screen(splash)  # <-- On centre APRÈS .show()

    sys.exit(app.exec())
