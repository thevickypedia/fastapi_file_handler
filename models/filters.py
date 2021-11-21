from logging import Filter, LogRecord


class EndpointFilter(Filter):
    """Class to initiate ``/docs`` filter in logs while preserving other access logs.

    >>> EndpointFilter

    """

    def filter(self, record: LogRecord) -> bool:
        """Filter out logging at ``/docs`` from log streams.

        Args:
            record: ``LogRecord`` represents an event which is created every time something is logged.

        Returns:
            bool:
            False flag for the endpoint that needs to be filtered.
        """
        return record.getMessage().find("/docs") == -1


class APIKeyFilter(Filter):
    """Class to initiate ``/investment`` filter in logs while preserving other access logs.

    >>> APIKeyFilter

    """

    def filter(self, record: LogRecord) -> bool:
        """Filter out logging at ``?apikey=`` from log streams.

        Args:
            record: ``LogRecord`` represents an event which is created every time something is logged.

        Returns:
            bool:
            False flag for the endpoint that needs to be filtered.
        """
        return record.getMessage().find("?apikey=") == -1
