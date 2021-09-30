from pydantic import BaseModel


class User(BaseModel):
    """
    User model

    Args:
        BaseModel (pydantic.BaseModel): Base model for pydantic
    """

    name: str
    email: str
    password: str


class ShowUser(BaseModel):
    """
    Show user model

    Args:
        BaseModel (pydantic.BaseModel): Base model for pydantic
    """

    name: str
    email: str

    class Config:
        """
        Config class for pydantic
        """

        orm_mode = True


class Login(BaseModel):
    """
    Login model

    Args:
        BaseModel (pydantic.BaseModel): Base model for pydantic
    """

    username: str
    password: str
