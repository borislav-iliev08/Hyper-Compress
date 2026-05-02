
import hashlib
from zipfile import ZipFile
from datetime import datetime

import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'database.txt')
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.ini')
USERS_FOLDER = os.path.join(BASE_DIR, 'users')


class Profile:
    def __init__(self, first_name, last_name, username, password_hash):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password_hash = password_hash

        self.user_folder = os.path.join(path_to_dir, 'users', self.username)
        self.history_file = os.path.join(self.user_folder, 'history.txt')
        personal_avatar = os.path.join(self.user_folder, 'avatar.png')

        if os.path.exists(personal_avatar):
            self.avatar_path = personal_avatar
        else:
            self.avatar_path = os.path.join(path_to_dir, 'images', 'default_avatar.png')

    def update_internal_paths(self, new_username):
        self.username = new_username
        self.user_folder = os.path.join(path_to_dir, 'users', self.username)
        self.history_file = os.path.join(self.user_folder, 'history.txt')
        personal_avatar = os.path.join(self.user_folder, 'avatar.png')
        if os.path.exists(personal_avatar):
            self.avatar_path = personal_avatar

    def get_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return f.readlines()
        return ["No history found."]

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if not value or (hasattr(self, 'first_name') and value == self.first_name):
            raise ValueError("Username is invalid or matches first name!")
        self._username = value


class Authentication:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _log_event(self, message):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path_to_logs, 'a', encoding='utf-8') as f:
            f.write(f"[{now}] {message}\n")

    def register_user(self, first_name, last_name, username, password):
        if len(password) < 3:
            raise ValueError("Password too short!")

        hashed = self.hash_password(password)

        if os.path.exists(path_to_database):
            with open(path_to_database, 'r', encoding='utf-8') as f:
                if any(f"|{username}|" in line for line in f if line.strip()):
                    raise Exception(f"User {username} already exists!")

        user_dir = os.path.join(path_to_dir, 'users', username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            with open(os.path.join(user_dir, 'history.txt'), 'w', encoding='utf-8') as f:
                f.write(f"History for {username} created on {datetime.now()}\n")

        with open(path_to_database, 'a', encoding='utf-8') as f:
            f.write(f"{first_name}|{last_name}|{username}|{hashed}\n")

        self._log_event(f"Registered user: {username}")

    def login(self, username, password):
        if not os.path.exists(path_to_database):
            raise Exception("No users registered yet.")

        hashed_attempt = self.hash_password(password)

        with open(path_to_database, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                parts = line.strip().split('|')
                if len(parts) == 4:
                    fn, ln, uname, passwd_hash = parts
                    if uname == username and passwd_hash == hashed_attempt:
                        self._log_event(f"Login success: {username}")
                        return Profile(fn, ln, uname, passwd_hash)

        self._log_event(f"Failed login attempt for: {username}")
        raise Exception("Invalid credentials!")

    @staticmethod
    def update_username(old_user, new_user):
        if not os.path.exists(path_to_database): return

        lines = []
        user_found = False

        with open(path_to_database, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                parts = line.strip().split('|')
                if parts[2] == new_user:
                    raise Exception("This username is already taken!")
                lines.append(parts)

        for parts in lines:
            if parts[2] == old_user:
                parts[2] = new_user
                user_found = True

        if not user_found:
            raise Exception("User not found in database!")

        old_path = os.path.join(path_to_dir, 'users', old_user)
        new_path = os.path.join(path_to_dir, 'users', new_user)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)

        with open(path_to_database, 'w', encoding='utf-8') as f:
            for p in lines:
                f.write("|".join(p) + "\n")

        Authentication()._log_event(f"Username changed: {old_user} -> {new_user}")

    @staticmethod
    def is_valid_session(profile):
        if not isinstance(profile, Profile) or not os.path.exists(path_to_database):
            return False
        with open(path_to_database, 'r', encoding='utf-8') as f:
            target = f"|{profile.username}|{profile.password_hash}"
            return any(target in line for line in f if line.strip())

class ZipManager:
    def __init__(self, working_dir, profile):
        if not Authentication.is_valid_session(profile):
            raise PermissionError("Access Denied: Unauthorized or Expired Session")

        self.working_dir = os.path.normpath(os.path.abspath(working_dir))
        self.profile = profile
        self.selected_paths = []


    def _log_to_file(self, msg):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.profile.history_file, 'a', encoding='utf-8') as f:
            f.write(f"{now} - {msg}\n")

    def create_archive_gui(self, name):
        timestamp = datetime.now().strftime("%Y-%m-%d-%H_%M")
        clean_name = name.replace('.zip', '')
        zip_filename = f"{clean_name}_{timestamp}.zip"

        full_zip_path = os.path.abspath(os.path.join(self.working_dir, zip_filename))

        if not self.selected_paths:
            raise ValueError("No items were selected for archiving!")

        try:
            with ZipFile(full_zip_path, 'w') as z:
                added_count = 0
                for item in self.selected_paths:
                    abs_item = os.path.abspath(item)

                    if not os.path.exists(abs_item):
                        continue

                    if abs_item == full_zip_path:
                        continue

                    if os.path.isfile(abs_item):
                        z.write(abs_item, os.path.basename(abs_item))
                        added_count += 1

                    elif os.path.isdir(abs_item):
                        base_name = os.path.basename(abs_item)
                        has_content = False

                        for root, dirs, files in os.walk(abs_item):
                            for file in files:
                                has_content = True
                                file_path = os.path.join(root, file)
                                if os.path.abspath(file_path) == full_zip_path:
                                    continue
                                arc_path = os.path.join(base_name, os.path.relpath(file_path, abs_item))
                                z.write(file_path, arc_path)
                                added_count += 1

                            for d in dirs:
                                dir_path = os.path.join(root, d)
                                if not os.listdir(dir_path):
                                    arc_dir_path = os.path.join(base_name, os.path.relpath(dir_path, abs_item)) + '/'
                                    z.write(dir_path, arc_dir_path)
                                    added_count += 1

                        if not has_content and not os.listdir(abs_item):
                            z.write(abs_item, base_name + '/')
                            added_count += 1

                if added_count == 0:
                    raise Exception("Selection resulted in 0 items. Archive is empty.")

            self._log_to_file(f"Created archive: {zip_filename} ({added_count} items)")
            return full_zip_path

        except Exception as e:
            if os.path.exists(full_zip_path):
                os.remove(full_zip_path)
            raise e
    def unzip_gui(self, zip_name):
        zip_path = os.path.join(self.working_dir, zip_name)
        extract_to = os.path.join(self.working_dir, zip_name.replace('.zip', ''))

        with ZipFile(zip_path, 'r') as z:
            z.extractall(path=extract_to)
        os.remove(zip_path)
        self._log_to_file(f"Extracted and deleted: {zip_name}")



if __name__ == "__main__":
    auth = Authentication()

    print("\n--- TEST 1: REGISTER DUPLICATE ---")
    try:
        auth.register_user('Ivan', 'Petrov', 'vankata', 'pass123')
        auth.register_user('Ivan', 'Petrov', 'vankata', 'pass123')
    except Exception as e:
        print("Expected fail:", e)

    print("\n--- TEST 2: LOGIN WRONG PASSWORD ---")
    try:
        auth.login('vankata', 'wrongpass')
    except Exception as e:
        print("Expected fail:", e)

    print("\n--- TEST 3: LOGIN CORRECT ---")
    try:
        session = auth.login('vankata', 'pass123')
        print("Login OK:", session.username)
    except Exception as e:
        print("Unexpected fail:", e)
        exit()

    print("\n--- TEST 4: SESSION BYPASS ATTEMPT ---")
    fake_profile = Profile("X", "Y", "fakeuser", "fakehash")
    try:
        ZipManager(r"D:\LoL", fake_profile)
        print("ERROR: bypass allowed")
    except Exception as e:
        print("Expected block:", e)

    print("\n--- TEST 5: ZIP FLOW ---")
    try:
        manager_zip = ZipManager(r"D:\LoL", session)
        manager_zip.list_and_select()
        manager_zip.create_archive()
    except Exception as e:
        print("ZIP ERROR:", e)

    print("\n--- TEST 6: UNZIP FLOW ---")
    try:
        manager_unzip = ZipManager(r"D:\LoL", session)
        manager_unzip.unzip_and_delete()
    except Exception as e:
        print("UNZIP ERROR:", e)

    print("\n--- TEST COMPLETE ---")