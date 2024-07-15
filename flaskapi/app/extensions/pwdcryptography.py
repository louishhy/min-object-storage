"""
Module for enhancing password cryptography.
"""

import bcrypt

def hash_password(password: str) -> tuple:
    """
    Using bcrypt algorithm to hash the password.

    :param password: The password to hash.
    :return: The hashed password and the salt, in format of (hashed_password, salt).
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password, salt

def check_password(provided_pwd, pwd_hash, salt) -> bool:
    """
    Check if the provided password is correct.

    :param provided_pwd: The provided password.
    :param pwd_hash: The hashed password.
    :param salt: The salt.
    :return: True if the password is correct, False otherwise.
    """
    salted_pwd = bcrypt.hashpw(provided_pwd.encode(), salt)
    return salted_pwd == pwd_hash