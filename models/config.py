from os import environ

from pydantic import BaseModel


class LogConfig(BaseModel):
    """Custom log configuration that matches uvicorn log format.

    >>> LogConfig

    See Also:
        - ``LOGGER_NAME`` should match the name passed to ``getLogger`` when this class is used for ``dictConfig``
        - ``LOG_FORMAT`` is set to match the format of ``uvicorn.access`` logs.
    """

    LOGGER_NAME: str = environ.get('module', __name__)
    LOG_FORMAT: str = '%(levelname)s:\t  %(message)s'
    LOG_LEVEL: str = "DEBUG"

    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": None,
        }
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }
