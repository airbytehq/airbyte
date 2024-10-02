class DownloaderError(Exception):
    """Generic error that could occur while downloading files"""


class DownloaderWarning(Exception):
    """Any 'exception' that we want to log as a warning"""


class StorageError(DownloaderError):
    """Raised when files cannot be read from or written to storage"""


class ThrottleError(DownloaderError):
    """Used if a network throttles a request"""


class ThrottleWarning(DownloaderWarning):
    """A 'ThrottleError' that we want to log as a warning"""


class AuthenticationError(DownloaderError):
    """Used when API returns 403"""


class ServerError(DownloaderError):
    """Used when API returns >=500"""


class TimeoutError(DownloaderError):
    """Raised when a request has timed out"""

class ConnectionError(DownloaderError):
    """Raised when a request has failed due to a connection error"""