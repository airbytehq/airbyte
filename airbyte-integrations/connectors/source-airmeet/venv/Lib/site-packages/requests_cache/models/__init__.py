"""Data models used to serialize response data"""

# ruff: noqa: F401
from typing import Union

from requests import PreparedRequest, Request, Response

from .base import RichMixin
from .raw_response import CachedHTTPResponse
from .request import CachedRequest
from .response import CachedResponse, DecodedContent, OriginalResponse

AnyResponse = Union[OriginalResponse, CachedResponse]
AnyRequest = Union[Request, PreparedRequest, CachedRequest]
AnyPreparedRequest = Union[PreparedRequest, CachedRequest]
