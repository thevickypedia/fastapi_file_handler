.. FileHandler API documentation master file, created by
   sphinx-quickstart on Sun Nov 21 13:20:14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to FileHandler API's documentation!
===========================================


.. toctree::
   :maxdepth: 2
   :caption: Read Me:

   README

FileHandler - APIKey Authentication
===================================

.. automodule:: auth_apikey
   :members:
   :undoc-members:

FileHandler - Server Authentication
===================================

.. automodule:: auth_server
   :members:
   :undoc-members:

FileHandler - Ultimate Uploader
===============================

.. automodule:: ultimate_uploader.upload
   :members:
   :undoc-members:

Models - Secrets
================

.. automodule:: models.secrets
   :members:
   :undoc-members:
   :exclude-members: USERNAME, PASSWORD

Models - Filters
================

.. autoclass:: models.filters.APIKeyFilter(logging.Filter)
   :members:
   :undoc-members:

.. autoclass:: models.filters.EndpointFilter(logging.Filter)
   :members:
   :undoc-members:

Models - Classes
================

.. autoclass:: models.classes.Bogus(tortoise.models.Model)
   :members:
   :undoc-members:
..
   :exclude-members: authentication

.. autoclass:: models.classes.DownloadHandler(pydantic.BaseModel)
   :members:
   :undoc-members:
..
   :exclude-members: FileName, FilePath

.. autoclass:: models.classes.ListHandler(pydantic.BaseModel)
   :members:
   :undoc-members:
..
   :exclude-members: FilePath

.. autoclass:: models.classes.UploadHandler(pydantic.BaseModel)
   :members:
   :undoc-members:
..
   :exclude-members: FileName, FilePath

Models - Executor
=================

.. autoclass:: models.executor.Executor(tortoise.models.Model)
   :members:
   :undoc-members:
   :exclude-members: LOGGER

Models - Custom Logging
=======================

.. autoclass:: models.config.LogConfig(pydantic.BaseModel)
   :members:
   :undoc-members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
