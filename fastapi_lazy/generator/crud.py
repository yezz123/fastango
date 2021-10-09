#!/usr/bin/python3
from os import environ

import jwt
from bson.objectid import ObjectId
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

SECRET_KEY = environ.get("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=environ.get("TOKEN_URL"))

db = environ.get("MONGODB_URL")


def verify_password(plain_password, hashed_password):
    """
    Verify a password against a hash using the pbkdf2_sha256 algorithm.
    Args:
        plain_password (str): The password to verify.
        hashed_password (str): The hashed password to verify against.
    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Generate a hash for a password using the pbkdf2_sha256 algorithm.
    Args:
        password (str): The password to hash.
    Returns:
        str: The hashed password.
    """
    return pbkdf2_sha256.hash(password)


class TokenData(BaseModel):
    """
    TokenData model
    Args:
        BaseModel (pydantic.BaseModel): Base model for pydantic
    """

    username: str = None


async def authenticate_user(username: str, password: str):
    """
    This function is used to authenticate a user.
    Args:
        username (str): The username of the user.
        password (str): The password of the user.
    Returns:
        dict: The user object.
    """
    user = await get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.get("password_hash")):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    This function is used to get the current user.
    Args:
        token (str, optional): The token of the user. Defaults to None.
    Raises:
        credentials_exception: If the token is invalid.
        credentials_exception: If the token is expired.
        credentials_exception: If the token is not found.
    Returns:
        dict: The user object.
    """
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = await db.users.find_one({"_id": ObjectId(token_data.username)})
    if user is None:
        raise credentials_exception
    return user


async def get_user(_db, username: str):
    """
    This function is used to get a user.
    Args:
        _db (pymongo.database.Database): The database object.
        username (str): The username of the user.
    Returns:
        dict: The user object.
    """
    user = await _db.users.find_one({"username": username})
    return user
