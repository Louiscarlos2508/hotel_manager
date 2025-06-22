import sys
from PySide6.QtWidgets import QApplication
from ui.splash import SplashScreen
from ui.login import LoginWindow

def show_login():
    login = LoginWindow()
    login.show()
    app.login_window = login

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashScreen(duration=3000, on_finish=show_login)
    splash.show()

    sys.exit(app.exec())
