import getpass
import os
import pwd

from tortoise.models import Model


class Secrets(Model):
    """Looks for the env vars ``USER`` and ``PASSWORD``, requests from the user if unavailable.

    >>> Secrets

    """

    USERNAME: str = os.environ.get('USER', os.path.expanduser('~') or pwd.getpwuid(os.getuid())[0] or os.getlogin())
    PASSWORD: str = os.environ.get('PASSWORD')

    if not USERNAME:
        USERNAME: str = input(__prompt='Enter username: ')
        os.environ['USER'] = USERNAME  # Store as env var so, value remains despite restart

    if not PASSWORD:
        PASSWORD: str = getpass.getpass(prompt='Enter PASSWORD: ')
        os.environ['PASSWORD'] = PASSWORD  # Store as env var so, value remains despite restart
