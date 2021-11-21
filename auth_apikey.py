from base64 import urlsafe_b64encode
from datetime import datetime
from logging import getLogger
from logging.config import dictConfig
from os import environ, listdir, path, stat
from pathlib import PurePath
from socket import gethostbyname
from uuid import uuid1

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from models.classes import (DownloadHandler, GetPhrase, ListHandler,
                            UploadHandler)
from models.filters import APIKeyFilter, EndpointFilter

__module__ = PurePath(__file__).stem
getLogger("uvicorn.access").addFilter(EndpointFilter())
getLogger("uvicorn.access").addFilter(APIKeyFilter())
LOGGER = getLogger(__module__)
environ['module'] = __module__

APIKEY = environ.get('APIKEY', urlsafe_b64encode(uuid1().bytes).rstrip(b'=').decode('ascii'))

app = FastAPI(
    title="FileHandler API",
    description="API to upload and download files to and from a server using a randomly generated uuid as apikey.",
    version="v1.0"
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


def verify_auth(apikey: str) -> None:
    """Authenticates the APIKEY.

    Args:
        apikey: Takes the APIKEY entered by the user as an argument.

    Raises:
        401: If auth fails.
    """
    if apikey != APIKEY:
        LOGGER.error(f'Authentication Failed: {apikey}')
        raise HTTPException(status_code=401, detail=status.HTTP_401_UNAUTHORIZED)
    LOGGER.info('Authentication Success')


@app.on_event(event_type='startup')
async def startup_event():
    """Runs during startup. Configures custom logging using LogConfig."""
    from models.config import LogConfig
    dictConfig(config=LogConfig().dict())
    LOGGER.info(f'Authentication Bearer: {APIKEY}')


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
    """Health Check for the server.

    Returns:
        dict:
        Health status in a dictionary.
    """
    return {'Message': 'Healthy'}


@app.get("/list-directory")
async def list_directory(feed: GetPhrase = Depends(), argument: ListHandler = Depends()) -> dict:
    """Lists all the files in a directory.

    Args:
        feed: Authentication apikey.
        argument: Takes the file path as an argument.

    Returns:
        dict:
        Returns a dictionary of files and directories in the given path.
    """
    verify_auth(apikey=feed.apikey)
    file_path = argument.FilePath

    if path.isfile(file_path):
        LOGGER.error(f'Not a directory: {file_path}')
        raise HTTPException(status_code=400, detail=status.HTTP_400_BAD_REQUEST)

    if file_path == '~':
        file_path = path.expanduser('~')
        dir_list = listdir(file_path)
    elif path.exists(file_path):
        dir_list = listdir(file_path)
    else:
        raise HTTPException(status_code=404, detail=status.HTTP_404_NOT_FOUND)

    LOGGER.info(f'Listing: {file_path}')
    file_listing = {"files": [entry for entry in dir_list if path.isfile(f'{file_path}{path.sep}{entry}')
                    if not entry.startswith('.')]}
    dir_listing = {"directories": [entry for entry in dir_list if path.isdir(f'{file_path}{path.sep}{entry}')
                   if not entry.startswith('.')]}
    if file_listing and dir_listing:
        return {file_path: dict(dir_listing, **file_listing)}  # Concatenates two dictionaries
    elif file_listing:
        return {file_path: file_listing}
    elif dir_listing:
        return {file_path: dir_listing}
    else:
        LOGGER.warning(f"No Content: {file_path}")
        raise HTTPException(status_code=204, detail=status.HTTP_204_NO_CONTENT)


@app.get("/download-file")
async def download_file(feed: GetPhrase = Depends(), argument: DownloadHandler = Depends()) -> FileResponse:
    """Asynchronously streams a file as the response.

    Args:
        feed: Takes the class **GetPhrase** as an argument.
        argument: Takes the class **DownloadHandler** as an argument.

    Returns:
        FileResponse:
        Returns the download-able version of the file.
    """
    verify_auth(apikey=feed.apikey)
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


@app.post("/upload-file")
async def upload_file(feed: GetPhrase = Depends(), upload: UploadHandler = Depends(), data: UploadFile = File(...)):
    """Allows the user to send a ``POST`` request to upload a file to the server.

    Args:
        feed: Authenticates the user.
        upload: Takes the class ``UploadHandler`` as an argument.
        data: Takes the file that has to be uploaded as an argument.

    Raises:
        200: If file was uploaded successfully.
        500: If the file was not stored.
    """
    verify_auth(apikey=feed.apikey)
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
