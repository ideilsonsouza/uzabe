import os
import ujson as json


class ZDCConfig:
    def __init__(self):
        self.const_file = '/db/database.json'

    def _load_file(self) -> dict:
        try:
            with open(self.const_file, 'r') as database:
                return json.load(database)
        except (OSError, ValueError, TypeError):
            return {}

    @staticmethod
    def load_datasource() -> dict:
        try:
            with open('/db/datasource.json', 'r') as datasource:
                return json.load(datasource)
        except (OSError, ValueError, TypeError):
            return {}

    def _save_file(self, data):
        try:
            with open(self.const_file, 'w') as database:
                json.dump(data, database)
        except (OSError, ValueError, TypeError) as e:
            print(f"Error saving data: {e}")

    @staticmethod
    def save_datasource(data: dict) -> bool:
        try:
            with open('/db/datasource.json', 'w') as datasource:
                json.dump(data, datasource)
            return True
        except (OSError, ValueError, TypeError) as e:
            print(f"Error saving datasource: {e}")
            return False

    def save_register(self, key, value):
        credentials = self._load_file()
        credentials[key] = value
        self._save_file(credentials)

    def verify_login_web(self, email, password):
        saved_email = self.load_register("sys_user")
        saved_password = self.load_register("sys_pass")
        return email == saved_email and password == saved_password

    def load_register(self, key, default=None):
        credentials = self._load_file()
        return credentials.get(key, default)

    def reset_register(self):
        if self.const_file in os.listdir():
            os.remove(self.const_file)