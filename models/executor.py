import logging
import math
import os
from typing import NoReturn

from fastapi import UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from tortoise.models import Model

from models.classes import (DownloadHandler, ListHandler,
                            MultiFileUploadHandler, UploadHandler)


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


class Executor(Model):
    """Base class to run all the executions when called.

    >>> Executor

    """

    LOGGER = logging.getLogger("LOGGER")

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

        if not os.path.isdir(file_path):
            self.LOGGER.error(f"Not a directory: {file_path}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{file_path} is not a directory.")

        if file_path == "~":
            file_path = os.path.expanduser("~")
            dir_list = os.listdir(file_path)
        elif os.path.exists(file_path):
            dir_list = os.listdir(file_path)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=status.HTTP_404_NOT_FOUND)

        self.LOGGER.info(f"Listing: {file_path}")
        file_listing = {"files": [entry for entry in dir_list if os.path.isfile(f"{file_path}{os.path.sep}{entry}")
                                  if not entry.startswith(".")]}
        dir_listing = {"directories": [entry for entry in dir_list if os.path.isdir(f"{file_path}{os.path.sep}{entry}")
                                       if not entry.startswith(".")]}
        if file_listing["files"] and dir_listing["directories"]:
            return {file_path: dict(dir_listing, **file_listing)}  # Concatenates two dictionaries
        elif file_listing["files"]:
            return {file_path: file_listing}
        elif dir_listing["directories"]:
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
        file_path = f"{argument.FilePath}{os.path.sep}{file_name}"
        if os.path.isfile(path=file_path):
            if file_name.startswith("."):
                self.LOGGER.warning(f"Access Denied: {file_name}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Dot (.) files cannot be downloaded over API.")
            else:
                self.LOGGER.info(f"Download Requested: {file_name}")
                return FileResponse(path=file_path, media_type="application/octet-stream", filename=file_name)
        else:
            self.LOGGER.error(f"File Not Found: {file_name}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"{status.HTTP_404_NOT_FOUND}\n{file_name}")

    async def execute_upload_file(self, file: UploadFile, argument: UploadHandler = None) -> None:
        """Executes task for the endpoint ``/upload-file``.

        Args:
            argument: Takes the class ``UploadHandler`` as an argument.
            file: Takes the file that has to be uploaded as an argument.

        Raises:
            HTTPExceptions:
            - 200: If file was uploaded successfully.
            - 500: If failed to upload file to server.
            - 404: If file path is null or does not exist.
        """
        if not (upload_path := argument.FilePath):
            self.LOGGER.error("Received a `null` value for upload filepath.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FilePath cannot be a `null` value")
        if not os.path.exists(upload_path):
            self.LOGGER.error(f"Upload path received doesn't exist: {upload_path}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UploadPath does not exist.")
        if not (filename := argument.FileName):
            filename = file.filename
        if upload_path.endswith(filename):
            filename = upload_path
        else:
            if upload_path.endswith(os.path.sep):
                filename = f"{upload_path}{filename}"
            else:
                filename = f"{upload_path}{os.path.sep}{filename}"
        content = await file.read()
        with open(filename, "wb") as f_stream:
            f_stream.write(content)

        file_name = filename.split(os.path.sep)[-1]
        if os.path.isfile(filename):
            self.LOGGER.info(f"Uploaded File: {file_name}")
            raise HTTPException(status_code=status.HTTP_200_OK, detail=f"{file_name} was uploaded to {upload_path}.")
        else:
            self.LOGGER.error(f"Failed to store: {file_name}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Unable to upload {filename} to {upload_path}.")

    async def execute_upload_files(self, files: list[UploadFile], argument: MultiFileUploadHandler = None) -> NoReturn:
        """Executes task for the endpoint ``/upload-files``.

        Args:
            argument: Takes the class ``MultiFileUploadHandler`` as an argument.
            files: Takes the list of files that has to be uploaded as an argument.

        Raises:
            HTTPExceptions:
            - 200: If file was uploaded successfully.
            - 404: If file path is null or does not exist.
        """
        if not (upload_path := argument.FilePath):
            self.LOGGER.error("Received a `null` value for upload filepath.")
            raise HTTPException(status_code=404, detail="FilePath cannot be a `null` value")
        if not os.path.exists(upload_path):
            self.LOGGER.error(f"Upload path received doesn't exist: {upload_path}")
            raise HTTPException(status_code=404, detail=status.HTTP_404_NOT_FOUND)
        return_val = {}
        if not [f for f in files if f.filename]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No input received.")
        for file in files:
            self.LOGGER.info(f"Downloading file: {file.filename} to server.")
            data = await file.read()
            with open(os.path.join(upload_path, file.filename), "wb") as file_stream:
                file_stream.write(data)
            if os.path.isfile(os.path.join(upload_path, file.filename)):
                self.LOGGER.info(f"Uploaded File: {file.filename}")
                return_val[file.filename] = size_converter(len(data))
            else:
                self.LOGGER.error(f"Failed to store: {file.filename}")
        raise HTTPException(status_code=status.HTTP_200_OK, detail=return_val)
