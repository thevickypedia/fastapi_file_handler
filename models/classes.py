from os import getcwd
from typing import Optional
from tortoise import fields
from tortoise.models import Model

from pydantic import BaseModel


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
