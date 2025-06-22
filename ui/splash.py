from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QColor, QPainter, QBrush, QLinearGradient, QGuiApplication


class SplashScreen(QWidget):
    def __init__(self, duration=3500, on_finish=None):
        super().__init__()

        self.duration = duration
        self.on_finish = on_finish

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        self.logo = QLabel()
        pixmap = QPixmap("assets/logo.png")  # Change ce chemin si nécessaire
        if not pixmap.isNull():
            self.logo.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Bienvenue à PALM BEACH Hôtel")
        self.title.setStyleSheet("color: white;")
        self.title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("Gestion & Réservations")
        self.subtitle.setStyleSheet("color: #dddddd; font-size: 14px; font-style: italic;")
        self.subtitle.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(15)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 7px;
                background-color: rgba(255, 255, 255, 30);
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b4db,
                    stop:1 #0083b0
                );
                border-radius: 7px;
            }
        """)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        layout.addWidget(self.logo)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_timer)
        self.timer.start(self.duration // 100)

        QTimer.singleShot(0, self.center_on_screen)

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        screen_geom = screen.availableGeometry()
        fg = self.frameGeometry()
        fg.moveCenter(screen_geom.center())
        self.move(fg.topLeft())

    def handle_timer(self):
        self.counter += 1
        self.progress.setValue(self.counter)
        if self.counter >= 100:
            self.timer.stop()
            self.close()
            if self.on_finish:
                self.on_finish()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 40, 85))
        gradient.setColorAt(1, QColor(0, 90, 150))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
