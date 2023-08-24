import os
import ujson as json
import ubinascii as binascii


class ZDCConfig:
    def __init__(self):
        self.const_file = '/db/database.json'

    def _load_file(self):
        try:
            with open(self.const_file, 'r') as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def _save_file(self, data):
        with open(self.const_file, 'w') as f:
            json.dump(data, f)

    def save_register(self, key, value, encode=True):
        credentials = self._load_file()
        if encode:
            credentials[key] = binascii.b2a_base64(value.encode()).decode().strip()
        else:
            credentials[key] = value
        self._save_file(credentials)

    def verify_login(self, email, password):
        saved_email = self.load_register("sys_user")
        saved_password = self.load_register("sys_password")
        return email == saved_email and password == saved_password

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