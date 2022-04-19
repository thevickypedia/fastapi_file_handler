"""Upload multiple files at once authenticating using http basic auth."""

# TODO: Remove serving HTML page and make it a proper backend.
# TODO: Interact with the JS in front-end and backend to show a progress bar in the UI.

import inspect
import logging
import os
import socket
from typing import Optional, Union

import uvicorn
from fastapi import (Cookie, FastAPI, File, HTTPException, Response, Security,
                     UploadFile, status)
from fastapi.responses import (HTMLResponse, JSONResponse, PlainTextResponse,
                               RedirectResponse)
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from models.executor import size_converter
from models.filters import EndpointFilter
from models.secrets import Secrets

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

security = HTTPBasic(realm="simple")
LOGGER = logging.getLogger("uvicorn")

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
upload_dir = os.path.join(current_dir, "uploads")

if not os.path.isdir(upload_dir):
    os.makedirs(upload_dir)

source_html = os.path.join(current_dir, "sources", "upload.html")
with open(source_html) as f_stream:
    HTML_CONTENT = f_stream.read()


@app.delete("/delete/file/{name_file}")
def delete_file(name_file: str) -> JSONResponse:
    """Deletes a file.

    Args:
        name_file: Takes name of the file to be deleted as an argument.

    Returns:
        JSONResponse:
        Deletion status wrapped in a JSON blurb.
    """
    try:
        os.remove(os.getcwd() + "/" + name_file)
        return JSONResponse(
            content={
                "removed": True
            },
            status_code=200
        )
    except FileNotFoundError:
        return JSONResponse(
            content={
                "removed": False,
                "error_message": "File not found"
            },
            status_code=404
        )


@app.post("/upload-files/", response_class=PlainTextResponse)
async def upload_files(files: list[UploadFile] = File(..., description="Upload files.")) -> Union[JSONResponse, str]:
    """Upload handler.

    Args:
        files: Takes list[UploadFile] as an argument. Use list[bytes] to upload using bytes.

    Returns:
        str:
        File names and the size of each file.
    """
    return_val = []
    if not [f for f in files if f.filename]:
        return JSONResponse(
            content={
                "error_message": "No input received."
            },
            status_code=404
        )
    for file in files:
        data = await file.read()
        with open(os.path.join(upload_dir, file.filename), 'wb') as file_stream:
            file_stream.write(data)
        return_val.append(
            f"{file.filename}{''.join([' ' for _ in range(60 - len(file.filename))])}{size_converter(len(data))}"
        )
    return "\n".join(return_val)


@app.get("/set/")
async def set_cookie(response: Response) -> bool:
    """Sets a cookie.

    Args:
        response: Takes the url response as an argument.

    Returns:
        bool:
        A simple boolean flag.
    """
    response.set_cookie(
        key="refresh_token",
        value="helloworld",
        httponly=True
    )
    return True


@app.get("/read/")
async def read_cookie(refresh_token: Optional[str] = Cookie(None)) -> JSONResponse:
    """Reads a cookie.

    Args:
        refresh_token: Name of the cookie.

    Returns:
        JSONResponse:
        Returns the value of the cookie as a json blurb.
    """
    if refresh_token:
        return JSONResponse(
            content={
                "refresh_token": refresh_token
            },
            status_code=200
        )
    else:
        return JSONResponse(
            content={
                "refresh_token": status.HTTP_404_NOT_FOUND
            },
            status_code=404
        )


@app.get("/login/", response_class=HTMLResponse)
async def login(credentials: HTTPBasicCredentials = Security(security)) -> HTMLResponse:
    """Login request handler.

    Args:
        credentials: HTTPBasicCredentials for authentication.

    Returns:
        HTMLResponse:
        HTMLResponse of the base upload page.
    """
    if not credentials.username and not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username and password are required to proceed.",
            headers={
                "WWW-Authenticate": "Basic"
            },
        )

    if credentials.username == Secrets.USERNAME and credentials.password == Secrets.PASSWORD:
        return HTMLResponse(
            content=HTML_CONTENT
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={
            "WWW-Authenticate": "Basic"
        },
    )


@app.get(path="/")
async def redirect_index() -> RedirectResponse:
    """Redirect to login page.

    Returns:
        RedirectResponse:
        Redirects the root endpoint ``/`` url to login page.
    """
    return RedirectResponse(url="/login")


if __name__ == '__main__':
    argument_dict = {
        "app": f"{__name__}:app",
        "host": socket.gethostbyname("localhost"),
        "port": int(os.environ.get("port", 1918)),
        "reload": True
    }
    uvicorn.run(**argument_dict)
