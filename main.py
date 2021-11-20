from os import environ
from socket import gethostbyname

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="FileHandler API",
    description="API to upload and download files to and from a server.",
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


if __name__ == '__main__':
    uvicorn.run(app="main:app", host=gethostbyname('localhost'), port=int(environ.get('port', 1914)), reload=True)
