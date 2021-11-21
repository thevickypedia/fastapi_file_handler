from base64 import urlsafe_b64encode
from logging import getLogger
from logging.config import dictConfig
from os import environ
from pathlib import PurePath
from socket import gethostbyname
from uuid import uuid1

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from models.classes import (DownloadHandler, GetPhrase, ListHandler,
                            UploadHandler)
from models.executor import Executor
from models.filters import APIKeyFilter, EndpointFilter

__module__ = PurePath(__file__).stem
getLogger("uvicorn.access").addFilter(EndpointFilter())
getLogger("uvicorn.access").addFilter(APIKeyFilter())
LOGGER = getLogger(__module__)
environ['module'] = __module__

APIKEY = environ.get('APIKEY', urlsafe_b64encode(uuid1().bytes).rstrip(b'=').decode('ascii'))
task_executor = Executor()

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
async def list_directory(feed: GetPhrase = Depends(),
                         argument: ListHandler = Depends()) -> dict:
    """Lists all the files in a directory.

    Args:
        feed: Authenticates the user request.
        argument: Takes the file path as an argument.

    Returns:
        dict:
        Returns a dictionary of files and directories in the given path.
    """
    verify_auth(apikey=feed.apikey)
    return await task_executor.execute_list_directory(argument=argument)


@app.get("/download-file")
async def download_file(feed: GetPhrase = Depends(),
                        argument: DownloadHandler = Depends()) -> FileResponse:
    """Asynchronously streams a file as the response.

    Args:
        feed: Authenticates the user request.
        argument: Takes the class **DownloadHandler** as an argument.

    Returns:
        FileResponse:
        Returns the download-able version of the file.
    """
    verify_auth(apikey=feed.apikey)
    return await task_executor.execute_download_file(argument=argument)


@app.post("/upload-file")
async def upload_file(feed: GetPhrase = Depends(),
                      upload: UploadHandler = Depends(),
                      data: UploadFile = File(...)) -> None:
    """Allows the user to send a ``POST`` request to upload a file to the server.

    Args:
        feed: Authenticates the user request.
        upload: Takes the class ``UploadHandler`` as an argument.
        data: Takes the file that has to be uploaded as an argument.

    Raises:
        200: If file was uploaded successfully.
        500: If the file was not stored.
    """
    verify_auth(apikey=feed.apikey)
    await task_executor.execute_upload_file(argument=upload, data=data)


if __name__ == '__main__':
    argument_dict = {
        "app": f"{__module__ or __name__}:app",
        "host": gethostbyname('localhost'),
        "port": int(environ.get('port', 1914)),
        "reload": True
    }
    uvicorn.run(**argument_dict)
