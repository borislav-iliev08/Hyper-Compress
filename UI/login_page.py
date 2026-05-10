from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLineEdit, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from qtwidgets import PasswordEdit
from main_logic import Authentication
import main_logic

auth_manager = Authentication()


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.card = QFrame()
        self.card.setObjectName("AuthCard")
        self.card.setFixedSize(400, 350)
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setSpacing(15)
        self.card_layout.setContentsMargins(30, 30, 30, 30)

        self.user_input = QLineEdit(placeholderText='Username')
        self.user_input.setObjectName("AuthInput")
        self.user_input.setFixedSize(300, 35)

        self.user_password = PasswordEdit()
        self.user_password.setObjectName("AuthInput")
        self.user_password.setPlaceholderText("Password")
        self.user_password.setFixedSize(300, 35)

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedSize(300, 20)

        self.log_button = QtWidgets.QPushButton("LOGIN")
        self.log_button.setObjectName("AuthSubmitBtn")
        self.log_button.setFixedSize(100, 25)

        self.card_layout.addStretch(1)
        self.card_layout.addWidget(self.user_input, alignment=Qt.AlignCenter)
        self.card_layout.addWidget(self.user_password, alignment=Qt.AlignCenter)
        self.card_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        self.card_layout.addWidget(self.log_button, alignment=Qt.AlignCenter)
        self.card_layout.addStretch(1)

        self.layout.addStretch(1)
        self.layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)

        self.log_button.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.user_input.text().strip()
        password = self.user_password.text().strip()

        if not username or not password:
            self.show_status("Username/Password required!", False)
            return

        try:
            p = self.auth_manager.login(username, password)
            self.show_status(f"Welcome, {p.username}!", True)

            QTimer.singleShot(1200, lambda: self.safe_switch_to_dashboard(p))
        except Exception as e:
            self.show_status(str(e), False)

    def show_status(self, text, success):
        self.status_label.setText(text)
        color = "#27ae60" if success else "#e74c3c"
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; background: transparent; border: none;")

    def safe_switch_to_dashboard(self, profile):
        win = self.window()
        if win and hasattr(win, 'switch_to_dashboard'):
            win.switch_to_dashboard(profile)
