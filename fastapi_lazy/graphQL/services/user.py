import os

from auth import auth_handler

basedir = os.path.abspath(os.path.dirname(__file__))

auth_expiretime = str(
    os.environ.get("AUTH_EXPIRETIME")
)  # TODO: AttributeError: 'NoneType' object has no attribute 'get'


def user_login(name):

    access_token = auth_handler.create_access_token(
        user_id=name, expiretime=auth_expiretime
    )

    return {"id": 1, "name": name, "token": access_token}
