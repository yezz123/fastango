from datetime import datetime, timedelta
from os import environ

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

SECRET_KEY = environ.get("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=environ.get("TOKEN_URL"))


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    """
    Create an access token from a dictionary of data.
    Args:
        data (dict): Dictionary of data to encode in the token.
        expires_delta (timedelta, optional): Time delta for token expiration. Defaults to None.
    Returns:
        str: Access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
