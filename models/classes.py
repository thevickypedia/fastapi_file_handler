from os import getcwd
from typing import Optional

from passlib.hash import bcrypt
from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model


class DownloadHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``DownloadHandler``.

    >>> DownloadHandler

    """

    FileName: str
    FilePath: str = getcwd()


class UploadHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``UploadHandler``.

    >>> UploadHandler

    """

    FileName: Optional[str]
    FilePath: str = getcwd()


class GetPhrase(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``GetPhrase``.

    >>> GetPhrase

    """

    apikey: str


class Bogus(Model):
    """Model that handles input data for the API which is treated as members for the class ``Bogus``.

    >>> Bogus

    """

    authentication: str = fields.CharField(50)


class Login(Model):
    """Creates a datastructure with keys, id, username and password_hash

    >>> Login

    """
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)


class CreateLogin(Model):
    """Creates a datastructure with keys, id, username and password

    >>> CreateLogin

    """
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password = fields.CharField(128)
