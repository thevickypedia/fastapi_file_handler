from datetime import datetime
from os import environ, path, stat
from socket import gethostbyname

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

app = FastAPI(
    title="FileHandler API",
    description="### API to upload and download files to and from a server.",
    version="v1.0"
)


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
async def download_file(file_name: str, file_path: str) -> FileResponse:
    """# Asynchronously streams a file as the response.

    ## Args:
        file_name: Name of the file to be downloaded.
        file_path: The location of the file.

    ## Returns:
    `FileResponse:`
    Returns the download-able version of the file.
    """
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
    filename = f'uploads{path.sep}{data.filename}'
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
