import hashlib


def password_hash(password: str):
    """
    Hash a password for storing.

    Args:
        password (str): the password to hash.

    Returns:
        str: the hashed password.
    """
    sha512_1 = hashlib.sha512(password.encode("utf-8")).hexdigest()
    sha512_2 = hashlib.sha512(sha512_1.encode("utf-8")).hexdigest()
    sha512_3 = hashlib.sha512(sha512_2.encode("utf-8")).hexdigest()
    md5_1 = hashlib.md5(sha512_3.encode("utf-8")).hexdigest()
    return hashlib.sha512(md5_1.encode("utf-8")).hexdigest()
