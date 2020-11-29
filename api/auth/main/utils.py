import secrets


def hex_generator():
    return secrets.token_hex(4)
