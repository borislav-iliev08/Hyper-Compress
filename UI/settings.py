import os
import shutil
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt, QStandardPaths
from main_logic import Authentication
from PyQt5 import QtWidgets
auth_manager = Authentication()


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
