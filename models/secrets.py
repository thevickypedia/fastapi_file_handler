from getpass import getpass
from os import environ, path, getlogin, getuid
from pwd import getpwuid

from tortoise.models import Model


class Secrets(Model):
    """Looks for the env vars ``USER`` and ``PASSWORD``, requests from the user if unavailable.

    >>> Secrets

    """
    USERNAME: str = environ.get('USER', path.expanduser('~') or getpwuid(getuid())[0] or getlogin())
    PASSWORD: str = environ.get('PASSWORD')

    if not USERNAME:
        USERNAME: str = input(__prompt='Enter username: ')
        environ['USER'] = USERNAME  # Store as env var so, value remains despite restart

    if not PASSWORD:
        PASSWORD: str = getpass(prompt='Enter PASSWORD: ')
        environ['PASSWORD'] = PASSWORD  # Store as env var so, value remains despite restart
