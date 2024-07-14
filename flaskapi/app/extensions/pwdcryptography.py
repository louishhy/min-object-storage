"""
Module for enhancing password cryptography.
"""

import bcrypt

def hash_password(password: str):
    """
    Returns hashed_password, salt tuple
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password, salt

def check_password(provided_pwd: str, pwd_hash, salt) -> bool:
    salted_pwd = bcrypt.hashpw(provided_pwd.encode(), salt)
    return salted_pwd == pwd_hash