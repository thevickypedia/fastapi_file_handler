from datetime import datetime
from logging import getLogger
from os import listdir, path, stat

from fastapi import UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from tortoise.models import Model

from models.classes import DownloadHandler, ListHandler, UploadHandler

LOGGER = getLogger(__name__)


class Executor(Model):
    """Base class to run all the executions when called.

    >>> Executor

    """

    @classmethod
    async def execute_list_directory(cls, argument: ListHandler) -> dict:
        """Executes task for the endpoint ``/list-directory``.

        Args:
            argument: Takes the class ``ListHandler`` as an argument.

        Returns:
            dict:
            Returns a dictionary of files and directories in the given path.
        """
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

    @classmethod
    async def execute_download_file(cls, argument: DownloadHandler) -> FileResponse:
        """Executes task for the endpoint ``/download-file``.

        Args:
            argument: Takes the class ``DownloadHandler`` as an argument.

        Returns:
            FileResponse:
            Returns the download-able version of the file.
        """
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

    @classmethod
    async def execute_upload_file(cls, argument: UploadHandler, data: UploadFile) -> None:
        """Executes task for the endpoint ``/upload-file``.

        Args:
            argument: Takes the class ``UploadHandler`` as an argument.
            data: Takes the file that has to be uploaded as an argument.
        """
        if not (filename := argument.FileName):
            filename = data.filename
        if (filepath := argument.FilePath) and (filepath.endswith(filename)):
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
