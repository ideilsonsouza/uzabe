import ubinascii as binascii

def decode_string(encoded_data):
    _strings = binascii.a2b_base64(encoded_data.encode()).decode()
    return _strings

def encode_string(data):
    _strings = binascii.b2a_base64(data.encode()).decode().strip()
    return _strings
