"""Modules that implement cache policy, based on a combination of standard HTTP headers and
additional settings and features specific to requests-cache.
"""

# ruff: noqa: E402,F401,F403
# isort: skip_file
from datetime import datetime, timedelta
from typing import Callable, Dict, Pattern as RegexPattern, Union, MutableMapping

from requests import Response

ExpirationTime = Union[None, int, float, str, datetime, timedelta]
ExpirationPattern = Union[  # Either a glob expression as str or a compiled regex pattern
    str,
    RegexPattern,
]
ExpirationPatterns = Dict[ExpirationPattern, ExpirationTime]
FilterCallback = Callable[[Response], bool]
KeyCallback = Callable[..., str]
HeaderDict = MutableMapping[str, str]


from .expiration import *
from .settings import *
from .directives import CacheDirectives, set_request_headers
from .actions import CacheActions
