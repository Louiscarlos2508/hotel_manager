import sys

from PySide6.QtWidgets import QApplication

from database.db import init_db
from ui.login import LoginWindow
from ui.splash import SplashScreen


def show_login():
    login = LoginWindow()
    login.show()
    app.login_window = login

if __name__ == "__main__":
    init_db()
    #BaseModel.connect()  # ⬅️ Connexion persistante à la DB

    app = QApplication(sys.argv)
    splash = SplashScreen(duration=3000, on_finish=show_login)
    splash.show()

    sys.exit(app.exec())
