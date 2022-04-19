import base64
# from base64 import urlsafe_b64encode
import logging.config
import os
import socket
import uuid
from typing import Any

import uvicorn
from fastapi import (Depends, FastAPI, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from models.classes import (DownloadHandler, ListHandler,
                            MultiFileUploadHandler, UploadHandler)
from models.executor import Executor
from models.filters import APIKeyFilter, EndpointFilter

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
logging.getLogger("uvicorn.access").addFilter(APIKeyFilter())
LOGGER = logging.getLogger("LOGGER")

APIKEY = os.environ.get('APIKEY', base64.urlsafe_b64encode(uuid.uuid1().bytes).rstrip(b'=').decode('ascii'))
task_executor = Executor()

app = FastAPI(
    title="FileHandler API",
    description="Vignesh's **FileHandler** API to upload and download files to and from a server using a apikey."
                "\n\n"
                "**Contact:** [https://vigneshrao.com/contact](https://vigneshrao.com/contact)",
    version="v1.0"
)

origins = [
    "http://localhost.com",
    "https://localhost.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\.loca\.lt/*",  # noqa: W605
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_auth(apikey: str) -> None:
    """Authenticates the APIKEY.

    Args:
        apikey: Takes the APIKEY entered by the user as an argument.

    Raises:
        HTTPExceptions:
        - 401: If authentication fails.
    """
    if apikey != APIKEY:
        LOGGER.error(f'Authentication Failed: {apikey}')
        raise HTTPException(status_code=401, detail=status.HTTP_401_UNAUTHORIZED)
    LOGGER.info('Authentication Success')


@app.on_event(event_type="startup")
async def startup_event():
    """Runs during startup. Configures custom logging using LogConfig."""
    from models.config import LogConfig
    logging.config.dictConfig(config=LogConfig().dict())
    LOGGER.info(f'Authentication Bearer: {APIKEY}')


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_index() -> str:
    """Redirect to documents.

    Returns:
        str:
        Redirects `/` url to `/docs`
    """
    return '/docs'


@app.get("/status/", include_in_schema=False)
def health() -> dict:
    """Health Check for the server.

    Returns:
        dict:
        Health status in a dictionary.
    """
    return {'Message': 'Healthy'}


@app.post("/list-directory/")
async def list_directory(apikey: Any = Form(...),
                         argument: ListHandler = Depends()) -> dict:
    """Lists all the files in a directory.

    Args:
        apikey: Authenticates the user request.
        argument: Takes the file path as an argument.

    Returns:
        dict:
        Returns a dictionary of files and directories in the given path.
    """
    await verify_auth(apikey=apikey)
    return await task_executor.execute_list_directory(argument=argument)


@app.post("/download-file/")
async def download_file(apikey: Any = Form(...),
                        argument: DownloadHandler = Depends()) -> FileResponse:
    """Asynchronously streams a file as the response.

    Args:
        apikey: Authenticates the user request.
        argument: Takes the class **DownloadHandler** as an argument.

    Returns:
        FileResponse:
        Returns the download-able version of the file.
    """
    await verify_auth(apikey=apikey)
    return await task_executor.execute_download_file(argument=argument)


@app.post("/upload-file/")
async def upload_file(apikey: Any = Form(...),
                      data: UploadFile = File(...),
                      upload: UploadHandler = Depends()) -> None:
    """Allows the user to send a ``POST`` request to upload a file to the server.

    Args:
        apikey: Authenticates the user request.
        upload: Takes the class ``UploadHandler`` as an argument.
        data: Takes the file that has to be uploaded as an argument.
    """
    await verify_auth(apikey=apikey)
    await task_executor.execute_upload_file(argument=upload, file=data)


@app.post("/upload-files/")
async def upload_files(apikey: Any = Form(...),
                       data: list[UploadFile] = File(...),
                       upload: MultiFileUploadHandler = Depends()) -> None:
    """Allows the user to send a ``POST`` request to upload a file to the server.

    Args:
        apikey: Authenticates the user request.
        upload: Takes the class ``UploadHandler`` as an argument.
        data: Takes the file that has to be uploaded as an argument.
    """
    await verify_auth(apikey=apikey)
    await task_executor.execute_upload_files(argument=upload, files=data)


if __name__ == '__main__':
    argument_dict = {
        "app": f"{__name__}:app",
        "host": socket.gethostbyname('localhost'),
        "port": int(os.environ.get('port', 1914)),
        "reload": True
    }
    uvicorn.run(**argument_dict)
