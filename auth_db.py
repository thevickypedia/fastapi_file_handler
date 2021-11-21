from logging import getLogger
from logging.config import dictConfig
from os import environ
from pathlib import PurePath
from socket import gethostbyname

import jwt
import uvicorn
from fastapi import FastAPI, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from passlib.hash import bcrypt
from tortoise.contrib.fastapi import register_tortoise

from models.authenticator import authenticate_user, get_current_user, JWT_SECRET
from models.classes import Login
from models.user_models import CustomModels

__module__ = PurePath(__file__).stem
LOGGER = getLogger(__module__)
environ['module'] = __module__
custom_models = CustomModels

app = FastAPI(
    title="UserAccounts",
    description="API to create and authenticate user profiles.",
    version="v1.0"
)


@app.on_event(event_type='startup')
async def startup_event():
    from models.config import LogConfig
    dictConfig(config=LogConfig().dict())


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def redirect_index() -> str:
    """Redirect to documents.

    Returns:
        str:
        Redirects `/` url to `/docs`
    """
    return '/docs'


@app.get('/status', include_in_schema=False)
def health() -> dict:
    """Health Check for FileFeeder.

    Returns:
        dict:
        Health status in a dictionary.
    """
    return {'Message': 'Healthy'}


@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """# Generates a jwt for the credentials received.

    ## Args:
        form_data: Takes the OAuth2PasswordRequestForm model as an argument.

    ## Returns:
        Returns a dictionary of access_token and token_type.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail=status.HTTP_401_UNAUTHORIZED)
    user_obj = await custom_models.User_Model.from_tortoise_orm(obj=user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    return {'access_token': token, 'token_type': 'bearer'}


# noinspection PyUnresolvedReferences
@app.post('/users', response_model=custom_models.User_Model)
async def create_user(user: custom_models.User_i_Model):
    """# Creates a new user profile and stores it in the database.

    ## Args:
        user: Takes the internal user profile model as an argument.

    ## Returns:
        Returns a PyDantic model.
    """
    user_obj = Login(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    LOGGER.info('sqlite3 db.UserProfiles')
    LOGGER.info('SELECT * FROM login;')
    return await custom_models.User_Model.from_tortoise_orm(obj=user_obj)


@app.get('/authenticate', response_model=custom_models.User_Model)
async def auth_user(user: custom_models.User_Model = Depends(get_current_user)):
    """# Authenticates any user per the information stored in the database.

    ## Args:
        user: Takes the User_Pydantic model as an argument.

    ## Returns:
        Returns the user profile information.

    ## See Also:
        This is just a placeholder, and a method for further development.
    """
    return user


register_tortoise(
    app=app,
    db_url='sqlite://db.UserProfiles',
    modules={
        'models': [__module__]
    },
    generate_schemas=True,
    add_exception_handlers=True
)

if __name__ == '__main__':
    argument_dict = {
        "app": f"{__module__ or __name__}:app",
        "host": gethostbyname('localhost'),
        "port": int(environ.get('port', 1914)),
        "reload": True
    }
    uvicorn.run(**argument_dict)
