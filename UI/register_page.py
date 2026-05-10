from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLineEdit, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from qtwidgets import PasswordEdit
from main_logic import Authentication
import main_logic

auth_manager = Authentication()


class RegisterPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.card = QFrame()
        self.card.setObjectName("AuthCard")
        self.card.setFixedSize(400, 450)
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setSpacing(15)
        self.card_layout.setContentsMargins(30, 30, 30, 30)

        self.f_name = QLineEdit(placeholderText='First Name')
        self.l_name = QLineEdit(placeholderText='Last Name')
        self.u_name = QLineEdit(placeholderText='Username')
        self.p_word = PasswordEdit(placeholderText='Password')
        self.c_word = PasswordEdit(placeholderText='Confirm Password')
        self.c_word.setEchoMode(QLineEdit.Password)

        self.inputs = [self.f_name, self.l_name, self.u_name, self.p_word, self.c_word]
        for i in self.inputs:
            i.setObjectName("AuthInput")
            i.setFixedSize(300, 35)
            self.card_layout.addWidget(i, alignment=Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedSize(300, 20)

        self.reg_button = QtWidgets.QPushButton('REGISTER')
        self.reg_button.setObjectName("AuthSubmitBtn")
        self.reg_button.setFixedSize(100, 25)

        self.card_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        self.card_layout.addWidget(self.reg_button, alignment=Qt.AlignCenter)

        self.layout.addStretch(1)
        self.layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)

        self.reg_button.clicked.connect(self.handle_register)

    def handle_register(self):
        d = [i.text().strip() for i in self.inputs]
        if not all(d):
            self.show_status("All fields are required!", False)
            return
        if d[3] != d[4]:
            self.show_status("Passwords mismatch!", False)
            return

        try:
            auth_manager.register_user(d[0], d[1], d[2], d[3])
            self.show_status("Registered successfully!", True)

            QTimer.singleShot(1200, self.safe_go_to_login)
        except Exception as e:
            self.show_status(str(e), False)

    def show_status(self, text, success):
        self.status_label.setText(text)
        color = "#27ae60" if success else "#e74c3c"
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; background: transparent; border: none;")

    def safe_go_to_login(self):
        win = self.window()
        if win and hasattr(win, 'clicked_login'):
            win.clicked_login()
