from typing import Any, List, Optional


class TransportError(Exception):
    """Base class for all the Transport exceptions"""

    pass


class TransportProtocolError(TransportError):
    """Transport protocol error.

    The answer received from the server does not correspond to the transport protocol.
    """


class TransportServerError(TransportError):
    """The server returned a global error.

    This exception will close the transport connection.
    """

    code: Optional[int]

    def __init__(self, message: str, code: Optional[int] = None):
        super(TransportServerError, self).__init__(message)
        self.code = code


class TransportQueryError(TransportError):
    """The server returned an error for a specific query.

    This exception should not close the transport connection.
    """

    query_id: Optional[int]
    errors: Optional[List[Any]]
    data: Optional[Any]
    extensions: Optional[Any]

    def __init__(
        self,
        msg: str,
        query_id: Optional[int] = None,
        errors: Optional[List[Any]] = None,
        data: Optional[Any] = None,
        extensions: Optional[Any] = None,
    ):
        super().__init__(msg)
        self.query_id = query_id
        self.errors = errors
        self.data = data
        self.extensions = extensions


class TransportClosed(TransportError):
    """Transport is already closed.

    This exception is generated when the client is trying to use the transport
    while the transport was previously closed.
    """


class TransportAlreadyConnected(TransportError):
    """Transport is already connected.

    Exception generated when the client is trying to connect to the transport
    while the transport is already connected.
    """
