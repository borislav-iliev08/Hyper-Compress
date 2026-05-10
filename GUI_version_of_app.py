import sys
import os
import ctypes
import configparser
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QStackedWidget)
from PyQt5.QtGui import QIcon, QPainter, QColor

from main_logic import Authentication
from UI.login_page import LoginPage
from UI.register_page import RegisterPage
from UI.dashboard import DashBoardMainApp

auth_manager = Authentication()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def draw_design_element(widget, painter):
    if not getattr(widget.window(), 'show_extra_details', False):
        return

    painter.setRenderHint(QPainter.Antialiasing)

    is_dark = getattr(widget.window(), 'current_theme_name', 'light') == 'dark'
    color = QColor(52, 152, 219, 40) if is_dark else QColor(100, 100, 100, 25)

    painter.setPen(Qt.NoPen)
    painter.setBrush(color)

    rect = widget.rect()
    painter.drawEllipse(rect.width() - 250, rect.height() - 250, 400, 400)
    painter.drawEllipse(rect.width() - 100, rect.height() - 350, 250, 250)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hype Compress')
        self.setGeometry(200, 100, 1300, 800)
        self.label = QLabel('HypeCompress')
        self.label.setObjectName("MainTitle")
        self.show_extra_details = False

        self.setWindowIcon(QIcon('images/logo.png'))

        self.config_file = 'settings.ini'
        self.config = configparser.ConfigParser()

        self.common_styles = """
            * { font-family: Arial; }
            #LicenseText { background: transparent; }
            #ChangeUserButton { padding: 10px; color: white; border-radius: 5px; background-color: #3498db; }
            #MainTitle { font-size: 24px; font-family: Arial Black; margin-bottom: 20px; }
            #PageHeader { font-size: 24px; font-weight: bold; }
            #AuthCard { border-radius: 20px; }
            #AuthInput { border-radius: 5px; padding: 8px; font-size: 14px; font-family: Arial; }
            #AuthInput:hover, #AuthInput:focus { border-radius: 10px; }
            #SidebarBtn { border: none; border-left: 5px solid transparent; text-align: left; padding: 12px 20px; font-size: 14px; font-weight: bold; outline: none; }
            #SidebarBtn:pressed { padding-left: 25px; }
            #MainList { border-radius: 10px; padding: 5px; }
            #SettingsTitle { font-size: 28px; font-weight: bold; }
            #SettingsSubHeader { font-weight: bold; font-size: 18px; }
            #SettingsCheckbox { font-weight: bold; font-size: 12px; }
            #ChangePicBtn { padding: 10px; color: white; border-radius: 5px; background-color: #3498db; }
            #BtnOpen { padding: 10px; color: white; border-radius: 5px; background-color: #f39c12; font-weight: bold; }
            #BtnArchive { padding: 10px; color: white; border-radius: 5px; background-color: #3498db; font-weight: bold; }
            #BtnExtract { padding: 10px; color: white; border-radius: 5px; background-color: #27ae60; font-weight: bold; }
            #StatusLabel { background: transparent; border: none; }
        """

        self.light_theme = self.common_styles + """
            QMainWindow { background-color: white; }
            

            QStackedWidget, QStackedWidget > QWidget, #FilesPage, #HistoryPage, SettingsPage { 
                background-color: transparent; 
            }
            #LicenseText { color: #2c3e50; background: transparent; }
            #AuthSubmitBtn:hover { background-color: #3498db; font-size: 10px; }
            #MainTitle { color: #2c3e50; }
            #AuthCard { background-color: rgba(192, 192, 192, 230); border: 2px solid rgba(169, 169, 169, 1); }
            #AuthInput { border: 2px solid #bdc3c7; background-color: white; color: black; }
            #Sidebar { background-color: #2c3e50; }
            #SidebarUsername { color: white; font-weight: bold; font-size: 14px; }
            #SidebarBtn { background-color: rgba(255, 255, 255, 30); color: white; }
            #AuthInput:hover, #AuthInput:focus { border: 2px solid black; }
            #MainList { border: 1px solid #ddd; background: rgba(255, 255, 255, 180); color: black; }
            #SidebarBtn:hover { background-color: #465f78; color: white; border-left: 5px solid #8a0b0f; }
            #PageHeader, #SettingsTitle { color: #2c3e50; }
            #SettingsSubHeader, #SettingsCheckbox { color: black; }
            #SidebarBtn:checked { background-color: #5a6773; color: white; border-left: 5px solid #03ad12; }
            #SettingsSubHeader { color: black; }

            #SettingsCheckbox { color: black; }
        """

        self.dark_theme = self.common_styles + """
            QMainWindow { background-color: #121212; }

            QStackedWidget, QStackedWidget > QWidget, #FilesPage, #HistoryPage, SettingsPage { 
                background-color: transparent; 
            }
            #SettingsSubHeader { color: #3498db; }
            #LicenseText { color: white; background: transparent; }

            #SettingsCheckbox { color: white; }
            #MainTitle { color: white; }
            #AuthCard { background-color: rgba(30, 30, 30, 230); border: 2px solid #333; }
            #AuthInput { border: 2px solid #444; background-color: #2d2d2d; color: white; }
            #Sidebar { background-color: #000000; }
            #SidebarUsername { color: #3498db; font-weight: bold; font-size: 14px; }
            #SidebarBtn { background-color: #1e1e1e; color: #aaa; }

            #MainList { border: 1px solid #333; background: rgba(30, 30, 30, 180); color: white; }
            #AuthSubmitBtn:hover { background-color: #3498db; font-size: 10px; }
            #AuthSubmitBtn { background-color: #333; color: white; }
            #PageHeader, #SettingsTitle { color: #3498db; }
            #SettingsSubHeader { color: #3498db; }
            #SettingsCheckbox { color: white; }
            #AuthInput:hover, #AuthInput:focus { border: 2px solid #3498db; }
            #SidebarBtn:hover { background-color: #333; color: white; border-left: 5px solid #8a0b0f; }
            #SidebarBtn:checked { background-color: #3498db; color: white; border-left: 5px solid #03ad12; }
        """
        """
            PROPRIETARY CODE BY BORISLAV ILIEV (C) 2026
            UNAUTHORIZED REMOVAL OF THIS HEADER IS A VIOLATION OF THE LICENSE.
            """


        self.load_settings()
        self.initUI()

    def save_settings(self, theme_name, details_isextra):
        if 'Settings' not in self.config: self.config['Settings'] = {}
        if 'Details' not in self.config: self.config['Details'] = {}

        self.config['Settings']['theme'] = theme_name
        self.config['Details']['details'] = str(details_isextra)
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def load_settings(self):
        self.config.read(self.config_file)
        theme = self.config.get('Settings', 'theme', fallback='light')
        self.current_theme_name = theme
        if theme == 'dark':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        self.show_extra_details = self.config.getboolean('Details', 'details', fallback=False)

    def apply_light_theme(self):
        self.setStyleSheet(self.light_theme)
        self.current_theme_name = "light"

    def apply_dark_theme(self):
        self.setStyleSheet(self.dark_theme)
        self.current_theme_name = "dark"

    def initUI(self):
        self.central = QWidget();
        self.setCentralWidget(self.central);
        self.layout = QVBoxLayout(self.central)

        self.label.setAlignment(Qt.AlignCenter)


        self.btn_layout = QHBoxLayout()
        self.login_btn = QtWidgets.QPushButton('Login');
        self.reg_btn = QtWidgets.QPushButton('Register')
        self.login_btn.setFixedSize(200, 33);
        self.reg_btn.setFixedSize(200, 33)

        self.btn_layout.addStretch(1)
        self.btn_layout.addWidget(self.login_btn)
        self.btn_layout.addWidget(self.reg_btn)
        self.btn_layout.addStretch(1)

        self.stack = QStackedWidget()
        self.login_scr = LoginPage()
        self.reg_scr = RegisterPage()
        self.login_scr.auth_manager = auth_manager
        self.reg_scr.auth_manager = auth_manager

        self.stack.addWidget(self.login_scr)
        self.stack.addWidget(self.reg_scr)


        self.layout.addStretch(1);
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.btn_layout)
        self.layout.addWidget(self.stack)
        self.layout.addStretch(5)
        self.login_btn.clicked.connect(self.clicked_login)
        self.reg_btn.clicked.connect(self.clicked_register)
        self.clicked_login()

    def clicked_login(self):
        self.stack.setCurrentIndex(0)
        self.login_btn.setStyleSheet(
            "background-color: #3498db; color: white; border-radius: 5px; font-family: Verdana; font-weight: bold; font-size: 13px;")
        self.reg_btn.setStyleSheet(
            "background-color: #ecf0f1; color: black; border-radius: 5px; border: 1px solid black; font-family: Verdana; font-weight: bold; font-size: 13px;")

    def clicked_register(self):
        self.stack.setCurrentIndex(1)
        self.reg_btn.setStyleSheet(
            "background-color: #3498db; color: white; border-radius: 5px; font-family: Verdana; font-weight: bold; font-size: 13px;")
        self.login_btn.setStyleSheet(
            "background-color: #ecf0f1; color: black; border-radius: 5px; border: 1px solid black; font-family: Verdana; font-weight: bold; font-size: 13px;")

    def switch_to_dashboard(self, profile):
        self.dash = DashBoardMainApp(profile, self)
        self.stack.addWidget(self.dash)
        self.label.hide()
        self.login_btn.hide()
        self.reg_btn.hide()
        self.stack.setCurrentWidget(self.dash)

    def paintEvent(self, event):
        if not self.show_extra_details:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.current_theme_name == "dark":
            color = QColor(52, 152, 219, 50)
        else:
            color = QColor(0, 0, 0, 15)

        painter.setPen(Qt.NoPen)
        painter.setBrush(color)


        w, h = self.width(), self.height()
        painter.drawEllipse(w - 450, h - 450, 600, 600)
        painter.drawEllipse(w - 250, h - 600, 400, 400)
        painter.drawEllipse(-100, h - 300, 400, 400)


def window():

    app = QApplication(sys.argv)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mycompany.HypeCompress.v1")
    app_icon = QIcon('images/logo.png')
    app.setWindowIcon(app_icon)
    win = App()
    win.show()
    sys.exit(app.exec_())

window()