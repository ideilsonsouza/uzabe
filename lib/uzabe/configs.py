import os
import ujson as json
import ubinascii as binascii


class ZDCConfig:
    def __init__(self):
        self.const_file = '/db/database.json'

    def _load_file(self)-> dict:
        try:
            with open(self.const_file, 'r') as database:
                return json.load(database)
        except (OSError, ValueError):
            return {}

    @staticmethod
    def load_datasource() -> dict:
        try:
            with open('/db/datasource.json', 'r') as datasource:
                return json.load(datasource)
        except (OSError, ValueError):
            return {}

    def _save_file(self, data):
        with open(self.const_file, 'w') as database:
            json.dump(data, database)

    @staticmethod
    def save_datasource(data: dict) -> bool:
        if data:
            try:
                with open('/db/datasource.json', 'w') as datasource:
                    json.dump(data, datasource)
                return True
            except (OSError, ValueError):
                return False

    def save_register(self, key, value, encode=True):
        credentials = self._load_file()
        if encode:
            credentials[key] = binascii.b2a_base64(value.encode()).decode().strip()
        else:
            credentials[key] = value
        self._save_file(credentials)

    def verify_login_web(self, email, password):
        saved_email = self.load_register("sys_user")
        saved_password = self.load_register("sys_pass")
        if email == saved_email and password == saved_password:
            return True
        else:
            return False

    def load_register(self, key, default=None, decode=True):
        credentials = self._load_file()
        value = credentials.get(key, default)

        if not decode or value is None or not isinstance(value, str):
            return value
        try:
            return binascii.a2b_base64(value.encode()).decode()

        except Exception as e:
            print(f"#: {e}")
            return default

    def reset_register(self):
        if self.const_file in os.listdir():
            os.remove(self.const_file)
