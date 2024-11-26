# Make sure to place exceptions first as they're dependencies of other imports.
import contextlib
from ._exceptions import VersionMismatch as VersionMismatch
from ._exceptions import DaggerError as DaggerError
from ._exceptions import ProvisionError as ProvisionError
from ._exceptions import DownloadError as DownloadError
from ._exceptions import SessionError as SessionError
from ._exceptions import ClientError as ClientError
from ._exceptions import ClientConnectionError as ClientConnectionError
from ._exceptions import TransportError as TransportError
from ._exceptions import ExecuteTimeoutError as ExecuteTimeoutError
from ._exceptions import InvalidQueryError as InvalidQueryError
from ._exceptions import QueryError as QueryError
from ._exceptions import ExecError as ExecError

# Make sure Config is first as it's a dependency in Connection.
from ._config import Config as Config
from ._config import Retry as Retry
from ._config import Timeout as Timeout

# We need the star import since this is a generated module.
from .client.gen import *
from ._connection import Connection as Connection
from ._connection import connection as connection
from ._connection import connect as connect
from ._connection import close as close

# Modules.
from .mod import Arg as Arg
from .mod import Doc as Doc
from .mod import field as field
from .mod import function as function
from .mod import object_type as object_type

# Re-export imports so they look like they live directly in this package.
for _value in list(locals().values()):
    if getattr(_value, "__module__", "").startswith("dagger."):
        with contextlib.suppress(AttributeError):
            _value.__module__ = __name__
