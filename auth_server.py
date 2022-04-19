import logging.config
import os
import socket

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models.classes import (Bogus, DownloadHandler, ListHandler,
                            MultiFileUploadHandler, UploadHandler)
from models.executor import Executor
from models.filters import EndpointFilter
from models.secrets import Secrets

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
LOGGER = logging.getLogger('LOGGER')

task_executor = Executor()

app = FastAPI(
    title="FileHandler API",
    description="**Description:** Vignesh's **FileHandler** to upload and download files to and from a server using "
                "the server's login credentials."
                "\n\n"
                "**Contact:** [https://vigneshrao.com/contact](https://vigneshrao.com/contact)",
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


@app.on_event(event_type="startup")
async def startup_event():
    """Runs during startup. Configures custom logging using LogConfig."""
    from models.config import LogConfig
    logging.config.dictConfig(config=LogConfig().dict())


@app.post("/authenticator/", include_in_schema=False)
async def server_authenticator(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """Authenticates the user entered information.

    Args:
        form_data: Takes the user input as an argument.

    Returns:
        dict:
        A dictionary of access token.

    Raises:
        HTTPExceptions:
        - 401: If user is unauthorized.
    """
    if form_data.username == Secrets.USERNAME and form_data.password == Secrets.PASSWORD:
        LOGGER.info('Authentication Successful')
        return {"access_token": form_data.username + form_data.password}
    else:
        LOGGER.error('Authentication failed')
        LOGGER.error(f'Username: {form_data.username}')
        LOGGER.error(f'Password: {form_data.password}')
        raise HTTPException(status_code=401, detail=status.HTTP_401_UNAUTHORIZED)


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_index() -> str:
    """Redirect to documents.

    Returns:
        str:
        Redirects `/` url to `/docs`
    """
    return "/docs"


@app.get("/status/", include_in_schema=False)
def health() -> dict:
    """Health Check for the server.

    Returns:
        dict:
        Health status in a dictionary.
    """
    return {'Message': 'Healthy'}


@app.get("/list-directory/")
async def list_directory(authenticator: dict = Depends(oauth2_scheme),
                         argument: ListHandler = Depends()) -> dict:
    """Lists all the files in a directory.

    Args:
        authenticator: Authenticates the user request.
        argument: Takes the file path as an argument.

    Returns:
        dict:
        Returns a dictionary of files and directories in the given path.
    """
    await Bogus(authentication=authenticator)
    return await task_executor.execute_list_directory(argument=argument)


@app.get("/download-file/")
async def download_file(authenticator: dict = Depends(oauth2_scheme),
                        argument: DownloadHandler = Depends()) -> FileResponse:
    """Asynchronously streams a file as the response.

    Args:
        authenticator: Authenticates the user request.
        argument: Takes the class **DownloadHandler** as an argument.

    Returns:
        FileResponse:
        Returns the download-able version of the file.
    """
    await Bogus(authentication=authenticator)
    return await task_executor.execute_download_file(argument=argument)


@app.post("/upload-file/")
async def upload_file(authenticator: dict = Depends(oauth2_scheme),
                      upload: UploadHandler = Depends(),
                      data: UploadFile = File(...)) -> None:
    """Allows the user to send a ``POST`` request to upload a file to the server.

    Args:
        authenticator: Authenticates the user request.
        upload: Takes the class `UploadHandler` as an argument.
        data: Takes the file that has to be uploaded as an argument.
    """
    await Bogus(authentication=authenticator)
    await task_executor.execute_upload_file(argument=upload, file=data)


@app.post("/upload-files/")
async def upload_files(authenticator: dict = Depends(oauth2_scheme),
                       upload: MultiFileUploadHandler = Depends(),
                       data: list[UploadFile] = File(...)) -> None:
    """Allows the user to send a ``POST`` request to upload multiple files to the server.

    Args:
        authenticator: Authenticates the user request.
        upload: Takes the class `UploadHandler` as an argument.
        data: Takes the file that has to be uploaded as an argument.
    """
    await Bogus(authentication=authenticator)
    await task_executor.execute_upload_files(argument=upload, files=data)


if __name__ == '__main__':
    argument_dict = {
        "app": f"{__name__}:app",
        "host": socket.gethostbyname('localhost'),
        "port": int(os.environ.get('port', 1918)),
        "reload": True
    }
    uvicorn.run(**argument_dict)
