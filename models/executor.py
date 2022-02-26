import os
from datetime import datetime
from logging import getLogger

from fastapi import UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from tortoise.models import Model

from models.classes import DownloadHandler, ListHandler, UploadHandler


class Executor(Model):
    """Base class to run all the executions when called.

    >>> Executor

    """

    LOGGER = getLogger('LOGGER')

    async def execute_list_directory(self, argument: ListHandler) -> dict:
        """Executes task for the endpoint ``/list-directory``.

        Args:
            argument: Takes the class ``ListHandler`` as an argument.

        Returns:
            dict:
            Returns a dictionary of files and directories in the given path.

        Raises:
            HTTPExceptions:
            - 400: If a file name is specified instead of file path.
            - 404: If the file path doesn't exist.

        See Also:
                Detail not specified for ``204`` since, any response to a ``HEAD`` request and any response with a
                ``1xx`` (Informational), ``204`` (No Content), or ``304`` (Not Modified) status codes are always
                terminated by the first empty line after the header fields, regardless of the header fields present
                in the message, and thus cannot contain a message body.
        """
        file_path = argument.FilePath

        if os.path.isfile(file_path):
            self.LOGGER.error(f'Not a directory: {file_path}')
            raise HTTPException(status_code=400, detail=status.HTTP_400_BAD_REQUEST)

        if file_path == '~':
            file_path = os.path.expanduser('~')
            dir_list = os.listdir(file_path)
        elif os.path.exists(file_path):
            dir_list = os.listdir(file_path)
        else:
            raise HTTPException(status_code=404, detail=status.HTTP_404_NOT_FOUND)

        self.LOGGER.info(f'Listing: {file_path}')
        file_listing = {"files": [entry for entry in dir_list if os.path.isfile(f'{file_path}{os.path.sep}{entry}')
                                  if not entry.startswith('.')]}
        dir_listing = {"directories": [entry for entry in dir_list if os.path.isdir(f'{file_path}{os.path.sep}{entry}')
                                       if not entry.startswith('.')]}
        if file_listing['files'] and dir_listing['directories']:
            return {file_path: dict(dir_listing, **file_listing)}  # Concatenates two dictionaries
        elif file_listing['files']:
            return {file_path: file_listing}
        elif dir_listing['directories']:
            return {file_path: dir_listing}
        else:
            self.LOGGER.info(f"No Content: {file_path}")
            return {"status_code": status.HTTP_204_NO_CONTENT, "detail": "No Content"}

    async def execute_download_file(self, argument: DownloadHandler) -> FileResponse:
        """Executes task for the endpoint ``/download-file``.

        Args:
            argument: Takes the class ``DownloadHandler`` as an argument.

        Returns:
            FileResponse:
            Returns the download-able version of the file.

        Raises:
            HTTPExceptions:
            - 403: If a dot (.) file is requested.
            - 404: If the file doesn't exist.
        """
        file_name = argument.FileName
        file_path = f'{argument.FilePath}{os.path.sep}{file_name}'
        if os.path.isfile(path=file_path):
            if file_name.startswith('.'):
                self.LOGGER.warning(f'Access Denied: {file_name}')
                raise HTTPException(status_code=403, detail='Dot (.) files cannot be downloaded over API.')
            else:
                self.LOGGER.info(f'Download Requested: {file_name}')
                return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
        else:
            self.LOGGER.error(f'File Not Found: {file_name}')
            raise HTTPException(status_code=404, detail=f'{status.HTTP_404_NOT_FOUND}\n{file_name}')

    async def execute_upload_file(self, data: UploadFile, argument: UploadHandler = None) -> None:
        """Executes task for the endpoint ``/upload-file``.

        Args:
            argument: Takes the class ``UploadHandler`` as an argument.
            data: Takes the file that has to be uploaded as an argument.

        Raises:
            HTTPExceptions:
            - 200: If file was uploaded successfully.
            - 500: If failed to upload file to server.
            - 404: If file path is null or does not exist.
        """
        if not (filepath := argument.FilePath):
            raise HTTPException(status_code=404, detail='FilePath cannot be a `null` value')
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=status.HTTP_404_NOT_FOUND)
        if not (filename := argument.FileName):
            filename = data.filename
        if filepath.endswith(filename):
            filename = filepath
        else:
            if filepath.endswith(os.path.sep):
                filename = f'{filepath}{filename}'
            else:
                filename = f'{filepath}{os.path.sep}{filename}'
        content = await data.read()
        with open(filename, 'wb') as file:
            file.write(content)

        file_name = filename.split(os.path.sep)[-1]
        if os.path.isfile(filename):
            if not int(datetime.now().timestamp()) - int(os.stat(filename).st_mtime):
                self.LOGGER.info(f'Uploaded File: {file_name}')
                raise HTTPException(status_code=200, detail=f'{file_name} was uploaded to {filepath}.')
            else:
                self.LOGGER.error(f'Failed to store: {file_name}')
                raise HTTPException(status_code=500, detail=f'Unable to store {filename} in the {filepath}.')
        else:
            self.LOGGER.error(f'Failed to store: {file_name}')
            raise HTTPException(status_code=500, detail=f'Unable to upload {filename} to {filepath}.')
