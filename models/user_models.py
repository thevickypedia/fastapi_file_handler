from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from models.classes import Login, CreateLogin


class CustomModels(Model):
    """Creates custom models using ``pydantic_model_creator`` for ``User_Model`` and ``User_i_Model``.

    >>> CustomModels

    See Also:
        - ``User_Model``: Used as supporting model for authentication.
        - ``User_i_Model``: Used only to create the main user profile.
    """
    User_Model = pydantic_model_creator(Login, name='user')
    User_i_Model = pydantic_model_creator(CreateLogin, name='UserIn', exclude_readonly=True)
