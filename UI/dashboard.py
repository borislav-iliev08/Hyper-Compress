import os
from PyQt5 import QtWidgets
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                             QPushButton, QStackedWidget, QListWidget,
                             QAbstractItemView, QProgressBar, QFileDialog)
from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon
from main_logic import Authentication, ZipManager
from UI.settings import SettingsPage
import base64
auth_manager = Authentication()







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
        if not selected:
            QtWidgets.QMessageBox.warning(self, "Warning", "No file selected!")
            return

        zips = [i.data(Qt.UserRole) for i in selected if i.text().lower().endswith('.zip')]

        if not zips:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select valid .zip files.")
            return

        for z in zips:
            if not os.path.exists(z):
                continue
            try:
                self.zip_logic.unzip_gui(z)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to extract {os.path.basename(z)}: {str(e)}")

        self.refresh_file_list()
