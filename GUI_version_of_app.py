import time
import os
import sys
import ctypes
import shutil
import configparser
from PyQt5 import QtWidgets, QtGui,QtSvg
from PyQt5.QtCore import Qt, QTimer, QStandardPaths
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QStackedWidget, QLabel,
                             QFrame, QFileDialog, QListWidget, QAbstractItemView, QProgressBar)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QRegion, QColor

from main_logic import Authentication, ZipManager
from qtwidgets import PasswordEdit

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


class SettingsPage(QWidget):
    def __init__(self, profile, parent_app, current_theme):
        super().__init__()
        self.profile, self.parent_app = profile, parent_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        self.title = QLabel("Settings")
        self.title.setObjectName("SettingsTitle")
        layout.addWidget(self.title)

        theme_group = QFrame()
        theme_layout = QVBoxLayout(theme_group)
        self.appearance_label = QLabel("Appearance")
        self.appearance_label.setObjectName("SettingsSubHeader")
        theme_layout.addWidget(self.appearance_label)

        self.dark_mode_cb = QtWidgets.QCheckBox("Dark Mode")
        self.dark_mode_cb.setObjectName("SettingsCheckbox")
        if current_theme == "dark":
            self.dark_mode_cb.setChecked(True)
        self.dark_mode_cb.toggled.connect(self.toggle_theme)

        self.mid_details_cb = QtWidgets.QCheckBox('Extra Details')
        self.mid_details_cb.setObjectName("SettingsCheckbox")
        self.mid_details_cb.setChecked(self.parent_app.parent_app.show_extra_details)
        self.mid_details_cb.toggled.connect(self.toggle_extra_details)

        theme_layout.addWidget(self.dark_mode_cb)
        theme_layout.addWidget(self.mid_details_cb)
        layout.addWidget(theme_group)

        profile_group = QFrame()
        prof_layout = QVBoxLayout(profile_group)
        self.prof_label = QLabel("Profile Settings")
        self.prof_label.setObjectName("SettingsSubHeader")
        prof_layout.addWidget(self.prof_label)

        self.btn_change_pic = QtWidgets.QPushButton("Change Profile Picture")
        self.btn_change_username = QtWidgets.QPushButton('Change Profile Username')
        self.btn_change_username.setObjectName('ChangeUserButton')
        self.btn_change_pic.setObjectName("ChangePicBtn")
        self.btn_change_pic.setFixedWidth(200)
        self.btn_change_username.setFixedWidth(200)

        self.btn_change_pic.clicked.connect(self.handle_change_pic)
        self.btn_change_username.clicked.connect(self.handle_username_change)

        prof_layout.addWidget(self.btn_change_pic)
        prof_layout.addWidget(self.btn_change_username)
        layout.addWidget(profile_group)

        layout.addStretch()

    def toggle_theme(self, checked):
        win = self.window()
        if win and hasattr(win, 'save_settings'):
            theme_name = "dark" if checked else "light"
            if checked:
                win.apply_dark_theme()
            else:
                win.apply_light_theme()
            win.save_settings(theme_name, win.show_extra_details)

    def handle_change_pic(self):
        pictures_path = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Avatar", pictures_path, "Images (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                target_path = os.path.join(self.profile.user_folder, 'avatar.png')
                if not os.path.exists(os.path.dirname(target_path)): os.makedirs(os.path.dirname(target_path))
                shutil.copy(file_path, target_path)
                self.profile.avatar_path = target_path
                self.parent_app.update_nav_avatar()
            except:
                pass

    def handle_username_change(self):

        new_username, ok = QtWidgets.QInputDialog.getText(
            self, "Change Username", "Enter new username:", QLineEdit.Normal, self.profile.username
        )

        if not ok or not new_username.strip() or new_username == self.profile.username:
            return

        try:
            auth_manager.update_username(self.profile.username, new_username)
            self.profile.update_internal_paths(new_username)
            self.parent_app.update_sidebar_info()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    def toggle_extra_details(self, checked):
        win = self.window()
        if win and hasattr(win, 'save_settings'):
            win.show_extra_details = checked
            win.update()
            win.save_settings(win.current_theme_name, checked)

class DashBoardMainApp(QWidget):
    def __init__(self, profile, parent_app):
        super().__init__()
        self.profile, self.parent_app, self.current_path = profile, parent_app, ""

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 30, 15, 30)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        self.update_sidebar_avatar()

        self.name_label = QLabel(f"@{self.profile.username}")
        self.name_label.setObjectName("SidebarUsername")
        self.name_label.setAlignment(Qt.AlignCenter)

        self.sidebar_layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.name_label, alignment=Qt.AlignCenter)
        self.sidebar_layout.addSpacing(40)

        self.sidebar_group = QtWidgets.QButtonGroup(self)
        self.btn_files = QtWidgets.QPushButton(" 📁 Files")
        self.btn_history = QtWidgets.QPushButton(" 📜 History")
        self.btn_settings = QtWidgets.QPushButton(" ⚙️ Settings")
        self.btn_license = QtWidgets.QPushButton('⚖️ License')

        for b in [self.btn_files, self.btn_history,self.btn_license, self.btn_settings]:
            b.setObjectName("SidebarBtn")
            b.setCheckable(True)
            self.sidebar_group.addButton(b)
            self.sidebar_layout.addWidget(b)

        self.sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()

        self.files_page = QWidget()
        self.files_page.setObjectName("FilesPage")
        files_layout = QVBoxLayout(self.files_page)
        files_layout.setContentsMargins(30, 30, 30, 30)
        files_layout.setSpacing(15)

        self.header = QLabel("File Manager")
        self.header.setObjectName("PageHeader")

        self.file_list = QListWidget()
        self.file_list.setObjectName("MainList")
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        actions_layout = QHBoxLayout()
        self.btn_open = QtWidgets.QPushButton(" 📂 Open/Enter")
        self.btn_open.setObjectName("BtnOpen")
        self.btn_archive = QtWidgets.QPushButton(" 📦 Archive")
        self.btn_archive.setObjectName("BtnArchive")
        self.btn_extract = QtWidgets.QPushButton(" 📂 Extract")
        self.btn_extract.setObjectName("BtnExtract")

        for b in [self.btn_open, self.btn_archive, self.btn_extract]:
            actions_layout.addWidget(b)

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()

        files_layout.addWidget(self.header)
        files_layout.addWidget(self.file_list)
        files_layout.addLayout(actions_layout)
        files_layout.addWidget(self.progress_bar)
        self.license_page = QWidget()
        self.license_page.setObjectName("LicensePage")
        lic_layout = QVBoxLayout(self.license_page)
        lic_layout.setContentsMargins(30, 30, 30, 30)



        l_header = QLabel("Software License")
        l_header.setObjectName("PageHeader")
        lic_layout.addWidget(l_header)
        self.lic_card = QFrame()
        self.lic_card.setObjectName("AuthCard")
        self.lic_card.setMinimumHeight(400)
        card_layout = QVBoxLayout(self.lic_card)
        self.version = "v1.0.0 Stable"
        self.support_email = "borislav718@gmail.com"
        author_info = f"""
                <div style='text-align: center;'>  
                    <h1 style='color: #3498db; margin-bottom: 0;'>Hype Compress</h1>
                    <p style='font-size: 14px; color: #3498db;'>Professional Compression Tool</p>
                    <p style='font-size: 14px;'>{self.version}</p>
                    <p style='font-size: 14px;'>{self.support_email}</p>
                    <br><br>

                    <div style='border: 1px solid #3498db; padding: 25px; border-radius: 10px; background: rgba(0,0,0,0.6); min-height: 500px; color: white;'>
                        <p style='font-size: 18px; font-weight: bold;'>DEVELOPER</p>
                        <p style='font-size: 24px; color: #3498db;'>Borislav Ivanov Iliev</p>
                        <p style='font-size: 16px; font-style: italic;'>Yambol, Bulgaria</p>

                        <br><br>

                        <div style='text-align: justify; padding: 10px;'>
                            <p style='font-size: 12px; color: #E74C3C; line-height: 1.4; font-weight: bold; text-align: center; margin-bottom: 8px;'>
                                LEGAL NOTICE & PROPRIETARY RIGHTS WARNING
                            </p>
                            <p style='font-size: 11px; color: #E74C3C; line-height: 1.5; font-weight: bold;'>
                                This software and its source code are the exclusive intellectual property of the developer. 
                                Any unauthorized reproduction, modification, or redistribution of this product, 
                                including any attempts to decompile or reverse-engineer its core algorithms, is strictly prohibited. 
                                Claiming ownership or misrepresenting this software as a third-party product constitutes a 
                                serious violation of International Copyright Law and the Intellectual Property Acts of the Republic of Bulgaria.
                                Violators will be subject to immediate legal action and criminal prosecution to the maximum extent permitted by law.
                            </p>
                        </div>

                        <table width="100%" style="margin-top: 100px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
                            <tr>
                                <td align="left" style="font-size: 11px; font-weight: bold; color: white;">
                                    All Rights Reserved 2026
                                </td>
                                <td align="right" style="font-size: 11px; font-weight: bold; letter-spacing: 2px; color: white;">
                                    HYPE
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
                """
        self.lic_text = QLabel(author_info)
        self.lic_text.setObjectName("LicenseText")
        self.lic_text.setTextFormat(Qt.RichText)
        self.lic_text.setAlignment(Qt.AlignCenter)
        self.lic_text.setWordWrap(True)

        card_layout.addWidget(self.lic_text)
        lic_layout.addWidget(self.lic_card)
        lic_layout.addStretch()


        self.history_page = QWidget()
        self.history_page.setObjectName("HistoryPage")
        hist_layout = QVBoxLayout(self.history_page)
        hist_layout.setContentsMargins(30, 30, 30, 30)

        self.h_header = QLabel("Operation History")
        self.h_header.setObjectName("PageHeader")
        self.history_list = QListWidget()
        self.history_list.setObjectName("MainList")

        hist_layout.addWidget(self.h_header)
        hist_layout.addWidget(self.history_list)


        current_theme = getattr(self.parent_app, 'current_theme_name', 'light')
        self.settings_page = SettingsPage(self.profile, self, current_theme)
        self.settings_page.setObjectName("SettingsPage")

        self.content_stack.addWidget(self.files_page)
        self.content_stack.addWidget(self.history_page)
        self.content_stack.addWidget(self.license_page)
        self.content_stack.addWidget(self.settings_page)
        self.main_layout.addWidget(self.content_stack)

        self.zip_logic = ZipManager(os.getcwd(), self.profile)

        self.btn_files.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.btn_history.clicked.connect(lambda: [self.content_stack.setCurrentIndex(1), self.refresh_history()])
        self.btn_license.clicked.connect(lambda : self.content_stack.setCurrentIndex(2))
        self.btn_settings.clicked.connect(lambda: self.content_stack.setCurrentIndex(3))

        self.btn_open.clicked.connect(self.handle_open_request)
        self.btn_archive.clicked.connect(self.start_archive_sequence)
        self.btn_extract.clicked.connect(self.start_extract_sequence)
        self.file_list.itemDoubleClicked.connect(self.handle_open_request)

        self.btn_files.setChecked(True)
        self.refresh_file_list()

    def refresh_file_list(self):
        self.file_list.clear()
        if not self.current_path:
            import string
            from ctypes import windll
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    item = QtWidgets.QListWidgetItem(f"💽 Drive {letter}:\\")
                    item.setData(Qt.UserRole, f"{letter}:\\")
                    self.file_list.addItem(item)
                bitmask >>= 1
            return

        back = QtWidgets.QListWidgetItem("⬅️ .. Back")
        back.setData(Qt.UserRole, os.path.dirname(self.current_path))
        self.file_list.addItem(back)

        try:
            for n in os.listdir(self.current_path):
                full = os.path.join(self.current_path, n)
                icon = "📁 " if os.path.isdir(full) else "📄 "
                item = QtWidgets.QListWidgetItem(f"{icon}{n}")
                item.setData(Qt.UserRole, full)
                self.file_list.addItem(item)
        except Exception:
            pass

    def handle_open_request(self):
        item = self.file_list.currentItem()
        if not item or not item.data(Qt.UserRole): return
        path = item.data(Qt.UserRole)

        if "Back" in item.text():
            self.go_back()
        elif os.path.isdir(path):
            self.current_path = path
            self.zip_logic.working_dir = path
            self.refresh_file_list()

    def go_back(self):
        new = os.path.dirname(self.current_path)
        if new == self.current_path or len(self.current_path) <= 3:
            self.current_path = ""
        else:
            self.current_path = new
        self.zip_logic.working_dir = self.current_path or os.getcwd()
        self.refresh_file_list()

    def update_sidebar_avatar(self):
        p = os.path.join(self.profile.user_folder, 'avatar.png')
        if not os.path.exists(p): p = "images/default_avatar.png"
        if not os.path.exists(p): p = "images/oni.png"

        if os.path.exists(p):
            pix = QPixmap(p).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            out = QPixmap(80, 80)
            out.fill(Qt.transparent)
            painter = QPainter(out)
            painter.setRenderHint(QPainter.Antialiasing)
            mask = QtGui.QPainterPath()
            mask.addEllipse(0, 0, 80, 80)
            painter.setClipPath(mask)
            painter.drawPixmap(0, 0, pix)
            painter.end()
            self.avatar_label.setPixmap(out)



    def update_nav_avatar(self):
        self.update_sidebar_avatar()

    def refresh_history(self):
        self.history_list.clear()
        try:
            for line in self.profile.get_history():
                self.history_list.addItem(line.strip())
        except Exception:
            pass

    def update_sidebar_info(self):
        self.name_label.setText(f"@{self.profile.username}")

    def run_progress_bar(self, callback):
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.timer = QTimer(self)

        def step():
            if self.progress_bar.value() < 100:
                self.progress_bar.setValue(self.progress_bar.value() + 2)
            else:
                self.timer.stop()
                self.progress_bar.hide()
                callback()

        self.timer.timeout.connect(step)
        self.timer.start(30)

    def start_archive_sequence(self):
        self.run_progress_bar(self.run_archiving)

    def run_archiving(self):
        items = self.file_list.selectedItems() or [self.file_list.currentItem()]
        paths = [os.path.abspath(i.data(Qt.UserRole)) for i in items if
                 i and i.data(Qt.UserRole) and ".." not in i.text()]

        if not paths: return
        self.zip_logic.selected_paths = paths

        name, ok = QtWidgets.QInputDialog.getText(self, 'Archive', 'Archive Name:')
        if ok and name.strip():
            try:
                self.zip_logic.create_archive_gui(name.strip())
                self.refresh_file_list()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def start_extract_sequence(self):
        self.run_progress_bar(self.run_extraction)

    def run_extraction(self):
        selected = self.file_list.selectedItems()
        zips = [i.data(Qt.UserRole) for i in selected if i.text().lower().endswith('.zip')]

        if not zips:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select .zip files to extract.")
            return

        for z in zips:
            try:
                self.zip_logic.unzip_gui(z)
            except Exception as e:
                print(f"Extraction error: {e}")

        self.refresh_file_list()


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
            p = auth_manager.login(username, password)
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
        self.login_scr = LoginPage();
        self.reg_scr = RegisterPage();
        self.stack.addWidget(self.login_scr);
        self.stack.addWidget(self.reg_scr)

        self.layout.addStretch(1);
        self.layout.addWidget(self.label);
        self.layout.addLayout(self.btn_layout);
        self.layout.addWidget(self.stack);
        self.layout.addStretch(5)
        self.login_btn.clicked.connect(self.clicked_login);
        self.reg_btn.clicked.connect(self.clicked_register);
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
        self.dash = DashBoardMainApp(profile, self);
        self.stack.addWidget(self.dash)
        self.label.hide();
        self.login_btn.hide();
        self.reg_btn.hide();
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