from os import environ

import jwt
from jwt.exceptions import ExpiredSignatureError

SECRET_KEY = environ.get("SECRET_KEY")
EXPIRE_TIME = environ.get("EXPIRE_TIME")
ALGORITHM = environ.get("ALGORITHM")


def create_token(data):
    """
    Create a token

    Args:
        data (dict): data to be encoded in the token

    Returns:
        str: token
    """
    return jwt.encode(data, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token):
    """
    Verify a token

    Args:
        token (str): token to be verified

    Returns:
        dict: decoded token
    """
    try:
        return jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM, verify=True)
    except ExpiredSignatureError:
        return False
