import getpass
import inspect
import logging
import math
import os
import socket
from typing import Union, Optional

import uvicorn
from fastapi import Cookie, FastAPI, File, UploadFile, Response, Security, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from models.filters import EndpointFilter

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

security = HTTPBasic(realm="simple")
LOGGER = logging.getLogger('uvicorn')

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
upload_dir = os.path.join(parent_dir, 'uploads')

if not os.path.isdir(upload_dir):
    os.makedirs(upload_dir)

source_html = os.path.join(current_dir, "upload.html")
with open(source_html) as f_stream:
    HTML_CONTENT = f_stream.read()

USERNAME = os.environ.get('USERNAME', os.environ.get('USER', getpass.getuser()))
PASSWORD = os.environ.get('PASSWORD', 'uploader2022')


def size_converter(byte_size: int) -> str:
    """Gets the current memory consumed and converts it to human friendly format.

    Args:
        byte_size: Receives byte size as argument.

    Returns:
        str:
        Converted understandable size.
    """
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(byte_size, 1024)))
    return f"{round(byte_size / pow(1024, index), 2)} {size_name[index]}"


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


@app.get('/set')
async def set_cookie(response: Response) -> bool:
    """Sets a cookie.

    Args:
        response: Takes the url response as an argument.

    Returns:
        bool:
        A simple boolean flag.
    """
    response.set_cookie(
        key='refresh_token',
        value='helloworld',
        httponly=True
    )
    return True


@app.get('/read')
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


@app.get("/login", response_class=HTMLResponse)
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
                'WWW-Authenticate': 'Basic'
            },
        )

    if credentials.username == USERNAME and credentials.password == PASSWORD:
        return HTMLResponse(
            content=HTML_CONTENT
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={
            'WWW-Authenticate': 'Basic'
        },
    )


@app.get(path="/")
async def redirect_index() -> RedirectResponse:
    """Redirect to login page.

    Returns:
        RedirectResponse:
        Redirects the root endpoint ``/`` url to login page.
    """
    return RedirectResponse(url='/login')


if __name__ == '__main__':
    argument_dict = {
        "app": f"{__name__}:app",
        "host": socket.gethostbyname('localhost'),
        "port": int(os.environ.get('port', 1918)),
        "reload": True
    }
    uvicorn.run(**argument_dict)
