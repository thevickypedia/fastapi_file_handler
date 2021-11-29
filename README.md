# API File Handler
Upload and download files using FastAPI

### Usage
- [auth_apikey.py](https://github.com/thevickypedia/api_file_handler/blob/main/auth_apikey.py):
Authenticates using an APIKey that can be stored as an env var `APIKEY`. Defaults to a randomly generated url safe UUID.
- [auth_server.py](https://github.com/thevickypedia/api_file_handler/blob/main/auth_server.py):
Authenticates using the server's `USER` and `PASSWORD`. If password is not available as env var, requests from the user.

### PRO-Tip
- [jprq](https://github.com/azimjohn/jprq-python-client)
- [localtunnel](https://theboroer.github.io/localtunnel-www/)
- [ngrok](https://ngrok.com/docs)

### Coding Standards
Docstring format: [`Google`](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) <br>
Styling conventions: [`PEP 8`](https://www.python.org/dev/peps/pep-0008/) <br>
Clean code with pre-commit hooks: [`flake8`](https://flake8.pycqa.org/en/latest/) and 
[`isort`](https://pycqa.github.io/isort/)

### Linting
`PreCommit` will ensure linting, and the doc creation are run on every commit.

**Requirement**
<br>
`pip install --no-cache --upgrade sphinx pre-commit recommonmark`

**Usage**
<br>
`pre-commit run --all-files`

### Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html)

[https://thevickypedia.github.io/api_file_handler/](https://thevickypedia.github.io/api_file_handler/)

## License & copyright
&copy; Vignesh Sivanandha Rao

Licensed under the [MIT License](https://github.com/thevickypedia/Jarvis/blob/master/LICENSE)
