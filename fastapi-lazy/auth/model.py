from pydantic import BaseModel


class LazyUser(BaseModel):
    """
    A lazy user model.

    Args:
        BaseModel (pydantic.BaseModel): Base model class.
    """

    username: str
    password: str
    role: str
