import os
from typing import Optional

from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model

if not os.path.isdir('uploads'):
    os.makedirs('uploads')


class DownloadHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``DownloadHandler``.

    >>> DownloadHandler

    """

    FileName: str
    FilePath: str = os.path.expanduser('~')


class UploadHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``UploadHandler``.

    >>> UploadHandler

    """

    FileName: Optional[str]
    FilePath: str = os.path.join(os.getcwd(), 'uploads')


class ListHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class ``ListHandler``.

    >>> ListHandler

    """

    FilePath: str


class Bogus(Model):
    """Model that handles input data for the API which is treated as members for the class ``Bogus``.

    >>> Bogus

    """

    authentication: str = fields.CharField(50)
