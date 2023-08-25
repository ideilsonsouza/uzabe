import ubinascii as binascii
import time
import json

def decode_string(encoded_data):
    _strings = binascii.a2b_base64(encoded_data.encode()).decode()
    return _strings

def encode_string(data):
    _strings = binascii.b2a_base64(data.encode()).decode().strip()
    return _strings
class ZDCFunctions:
    def __init__(self):
        pass

    def try_function(self, function, message, retries=3):
        success = function()
        while not success and self._count < retries:
            self._count += 1
            print(f"{message} - Tentativa {self._count}")
            time.sleep(TIMEOUT)
            success = function()

        return success