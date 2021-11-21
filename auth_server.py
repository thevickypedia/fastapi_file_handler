from datetime import datetime
from logging import getLogger
from logging.config import dictConfig
from os import environ, path, stat
from pathlib import PurePath
from socket import gethostbyname

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models.classes import UploadHandler, DownloadHandler, Bogus
from models.secrets import Secrets

__module__ = PurePath(__file__).stem
LOGGER = getLogger(__module__)
environ['module'] = __module__

app = FastAPI(
    title="FileHandler API",
    description="API to upload and download files to and from a server using the server's login credentials.",
    version="v2.0"
)

origins = [
    "http://localhost.com",
    "https://localhost.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex='https://.*\.loca\.lt/*',  # noqa: W605
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authenticator")


@app.on_event(event_type='startup')
async def startup_event():
    from models.config import LogConfig
    dictConfig(config=LogConfig().dict())


@app.post("/authenticator", include_in_schema=False)
async def authenticator(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == Secrets.USERNAME and form_data.password == Secrets.PASSWORD:
        LOGGER.info('Authentication Successful')
        return {"access_token": form_data.username + form_data.password}
    else:
        LOGGER.error('Authentication failed')
        LOGGER.error(f'Username: {form_data.username}')
        LOGGER.error(f'Password: {form_data.password}')
        raise HTTPException(status_code=401, detail=status.HTTP_401_UNAUTHORIZED)


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


# noinspection PyShadowingNames
@app.get("/download_file")
async def download_file(argument: DownloadHandler = Depends(), authenticator: dict = Depends(oauth2_scheme)):
    """# Asynchronously streams a file as the response.

    ## Args:
    `argument:` Takes the class **DownloadHandler** as an argument.

    ## Returns:
    `FileResponse:`
    Returns the download-able version of the file.
    """
    await Bogus(authentication=authenticator)
    file_name = argument.FileName
    file_path = f'{argument.FilePath}{path.sep}{file_name}'
    if path.isfile(path=file_path):
        if file_name.startswith('.'):
            LOGGER.warning(f'Access Denied: {file_name}')
            raise HTTPException(status_code=403, detail='Dot (.) files cannot be downloaded over API.')
        else:
            LOGGER.info(f'Download Requested: {file_name}')
            return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
    else:
        LOGGER.error(f'File Not Found: {file_name}')
        raise HTTPException(status_code=404, detail=status.HTTP_404_NOT_FOUND)


# noinspection PyShadowingNames
@app.post("/upload_file")
async def upload_file(upload: UploadHandler = Depends(), data: UploadFile = File(...),
                      authenticator: dict = Depends(oauth2_scheme)):
    """# Allows the user to send a ``POST`` request to upload a file to the server.

    ## Args:
    - `upload:` Takes the class `UploadHandler` as an argument.
    - `data:` Takes the file that has to be uploaded as an argument.

    ## Raises:
        - 200: If file was uploaded successfully.
        - 500: If the file was not stored.
    """
    await Bogus(authentication=authenticator)
    if not (filename := upload.FileName):
        filename = data.filename
    if (filepath := upload.FilePath) and (filepath.endswith(filename)):
        filename = filepath
    else:
        if filepath.endswith(path.sep):
            filename = f'{filepath}{filename}'
        else:
            filename = f'{filepath}{path.sep}{filename}'
    content = await data.read()
    with open(filename, 'wb') as file:
        file.write(content)

    file_name = filename.split(path.sep)[-1]
    if path.isfile(filename):
        if not int(datetime.now().timestamp()) - int(stat(filename).st_mtime):
            LOGGER.info(f'Uploaded File: {file_name}')
            raise HTTPException(status_code=200, detail=f'{file_name} was uploaded to server.')
        else:
            LOGGER.error(f'Failed to store: {file_name}')
            raise HTTPException(status_code=500, detail=f'Unable to store {filename} in the server.')
    else:
        LOGGER.error(f'Failed to store: {file_name}')
        raise HTTPException(status_code=500, detail=f'Unable to upload {filename} to server.')


if __name__ == '__main__':
    argument_dict = {
        "app": f"{__module__ or __name__}:app",
        "host": gethostbyname('localhost'),
        "port": int(environ.get('port', 1914)),
        "reload": True
    }
    uvicorn.run(**argument_dict)
