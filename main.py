from datetime import datetime
from os import environ, path, stat, getcwd
from socket import gethostbyname

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(
    title="FileHandler API",
    description="API to upload and download files to and from a server.",
    version="v1.0"
)

origins = [
    "http://localhost.com",
    "https://localhost.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FileHandler(BaseModel):
    """BaseModel that handles input data for the API which is treated as members for the class FileHandler.

    >>> FileHandler

    """
    FileName: str
    FilePath: str = getcwd()


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def redirect_index() -> str:
    """Redirect to documents.

    Returns:
        str:
        Redirects `/` url to `/docs`
    """
    return '/docs'


@app.get('/status', include_in_schema=False)
def status() -> dict:
    """Health Check for FileFeeder.

    Returns:
        dict:
        Health status in a dictionary.
    """
    return {'Message': 'Healthy'}


@app.get("/download_file")
async def download_file(argument: FileHandler = Depends()) -> FileResponse:
    """# Asynchronously streams a file as the response.

    ## Args:
    argument: Takes the class `FileHandler` as an argument.

    ## Returns:
    `FileResponse:`
    Returns the download-able version of the file.
    """
    file_name = argument.FileName
    file_path = f'{argument.FilePath}{path.sep}{file_name}'
    if path.isfile(path=file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
    else:
        raise HTTPException(status_code=404, detail='File not present.')


@app.post("/upload_file")
async def upload_file(data: UploadFile = File(...)):
    """# Allows the user to send a ``POST`` request to upload a file to the server.

    ## Args:
        data: Takes the file that has to be uploaded as an argument.

    ## Raises:
        - 200: If file was uploaded successfully.
        - 500: If the file was not stored.
    """
    filename = data.filename
    content = await data.read()
    with open(filename, 'w') as file:
        file.write(content.decode(encoding='UTF-8'))

    if path.isfile(filename):
        if not int(datetime.now().timestamp()) - int(stat(filename).st_mtime):
            raise HTTPException(status_code=200, detail=f'{filename} was uploaded to server.')
        else:
            raise HTTPException(status_code=500, detail=f'Unable to store {filename} in the server.')
    else:
        raise HTTPException(status_code=500, detail=f'Unable to upload {filename} to server.')


if __name__ == '__main__':
    uvicorn.run(app="main:app", host=gethostbyname('localhost'), port=int(environ.get('port', 1914)), reload=True)
