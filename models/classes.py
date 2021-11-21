from os import environ, getcwd
from typing import Optional

from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model


class DownloadHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``DownloadHandler``.

    >>> DownloadHandler

    See Also:
        - `FileName`: Takes filename as value.
        - `FilePath`: Defaults to server's directory.
    """

    if not environ.get('COMMIT'):
        FileName: str
        FilePath: str = getcwd()


class UploadHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``UploadHandler``.

    >>> UploadHandler

    See Also:
        - `FileName`: Takes filename as an optional value.
        - `FilePath`: Defaults to server's directory.
    """

    if not environ.get('COMMIT'):
        FileName: Optional[str]
        FilePath: str = getcwd()


class ListHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``ListHandler``.

    >>> ListHandler

    See Also:
        - `FilePath`: Defaults to server's directory.
    """

    FilePath: str


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
