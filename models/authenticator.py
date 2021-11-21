from base64 import urlsafe_b64encode
from logging import getLogger
from os import environ
from typing import Union
from uuid import uuid1

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.classes import Login
from models.user_models import CustomModels

LOGGER = getLogger(__name__)
JWT_SECRET = environ.get('JWT_SECRET', urlsafe_b64encode(uuid1().bytes).rstrip(b'=').decode('ascii'))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='generate-token')


async def authenticate_user(username: str, password: str) -> Union[Login, bool]:
    """Authenticates the username and password.

    Args:
        username: Takes username entered as an argument.
        password: Takes password entered as an argument.

    Returns:
        Login:
        Returns the login class if the authentication is successful.
    """
    user = await Login.get(username=username)
    if not user:
        return False
    if not user.verify_password(password=password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Gets the current user information.

    Args:
        token: Takes the oauth token as an argument.

    Returns:
        Returns a ``pydantic`` model.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await Login.get(id=payload.get('id'))
    except jwt.exceptions.DecodeError as error:
        LOGGER.error(error.__class__.__name__)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid username or password')
    return await CustomModels.User_Model.from_tortoise_orm(obj=user)
