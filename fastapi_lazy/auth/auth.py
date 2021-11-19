from os import environ

from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from jwt import decode
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

KEY = environ.get("KEY", "secret")

# Authenticate Model
class LazyUser(BaseModel):
    """
    A lazy user model.

    Args:
        BaseModel (pydantic.BaseModel): Base model class.
    """

    username: str
    password: str
    role: str


class LazyAuth(HTTPBearer):
    """
    A custom authentication class that uses the JWT token to authenticate the user.

    Args:
        HTTPBearer (class): The class that handles the authentication.
    """

    async def __call__(self, request: Request) -> LazyUser:
        """
        The authentication method.

        Args:
            request (Request): The request object.

        Raises:
            HTTPException: If the token is invalid.

        Returns:
            LazyUser: The user object.
        """
        cred = await super().__call__(request)
        try:
            user = decode(cred.credentials, key=KEY, algorithms="HS256")
        except Exception as exp:
            """
            If the token is invalid, raise an HTTPException.

            Raises:
                HTTPException: If the token is invalid.
            """
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=str(exp),
            )
        return LazyUser(**user)


authentication_lazy = LazyAuth(
    scheme_name="Bearer",
    auto_error=False,
)
