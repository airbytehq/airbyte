from __future__ import annotations

from datetime import datetime, timedelta
from logging import getLogger
from typing import TYPE_CHECKING, Dict, List, Optional, Union

import attr
from attrs import define, field
from requests import PreparedRequest, Response
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict

from ..policy import ExpirationTime, add_tzinfo, get_expiration_datetime, utcnow
from . import CachedHTTPResponse, CachedRequest, RichMixin

if TYPE_CHECKING:
    from ..policy.actions import CacheActions

# Format used for __str__ only
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S %Z'

# Support RFC 7159: JSON body root element can be an object, array, or any of its primitive types
DecodedContent = Union[Dict, List, str, bool, int, float, None]

logger = getLogger(__name__)


@define(auto_attribs=False, repr=False, slots=False)
class BaseResponse(Response):
    """Wrapper class for responses returned by :py:class:`.CachedSession`. This mainly exists to
    provide type hints for extra cache-related attributes that are added to non-cached responses.
    """

    created_at: datetime = field(factory=utcnow)
    expires: Optional[datetime] = field(default=None)
    cache_key: str = ''  # Not serialized; set by BaseCache.get_response()
    revalidated: bool = False  # Not serialized; set by CacheActions.update_revalidated_response()

    @property
    def from_cache(self) -> bool:
        return False

    @property
    def is_expired(self) -> bool:
        return False


@define(auto_attribs=False, repr=False, slots=False, init=False)
class OriginalResponse(BaseResponse):
    """Wrapper class for non-cached responses returned by :py:class:`.CachedSession`"""

    def __init__(self, **kwargs):
        Response.__init__(self)
        self.__attrs_init__(**kwargs)

    @classmethod
    def wrap_response(cls, response: Response, actions: 'CacheActions') -> 'OriginalResponse':
        """Modify a response object in-place and add extra cache-related attributes"""
        if not isinstance(response, cls):
            response.__class__ = cls
            # Add expires and cache_key only if the response was written to the cache
            response.expires = None if actions.skip_write else actions.expires  # type: ignore
            response.cache_key = None if actions.skip_write else actions.cache_key  # type: ignore
            response.created_at = utcnow()  # type: ignore
        return response  # type: ignore


@define(auto_attribs=False, repr=False, slots=False)
class CachedResponse(RichMixin, BaseResponse):
    """A class that emulates :py:class:`requests.Response`, optimized for serialization"""

    _content: bytes = field(default=None)
    _decoded_content: DecodedContent = field(default=None)
    _next: Optional[CachedRequest] = field(default=None)
    cookies: RequestsCookieJar = field(factory=RequestsCookieJar)
    created_at: datetime = field(default=None)
    elapsed: timedelta = field(factory=timedelta)
    encoding: str = field(default=None)
    expires: Optional[datetime] = field(default=None, converter=add_tzinfo)
    headers: CaseInsensitiveDict = field(factory=CaseInsensitiveDict)
    history: List['CachedResponse'] = field(factory=list)  # type: ignore
    raw: CachedHTTPResponse = None  # type: ignore  # Not serialized; populated from CachedResponse attrs
    reason: str = field(default=None)
    request: CachedRequest = field(factory=CachedRequest)  # type: ignore
    status_code: int = field(default=0)
    url: str = field(default=None)

    def __attrs_post_init__(self):
        # Not using created_at field default due to possible bug on Windows with omit_if_default
        self.created_at = self.created_at or utcnow()
        # Re-initialize raw (urllib3) response after deserialization
        self.raw = self.raw or CachedHTTPResponse.from_cached_response(self)

    @classmethod
    def from_response(cls, response: Response, **kwargs) -> 'CachedResponse':
        """Create a CachedResponse based on an original Response or another CachedResponse object"""
        if isinstance(response, CachedResponse):
            obj = attr.evolve(response, **kwargs)
            obj._convert_redirects()
            return obj

        obj = cls(**kwargs)

        # Copy basic attributes
        for k in Response.__attrs__:
            setattr(obj, k, getattr(response, k, None))

        # Store request, raw response, and next response (if it's a redirect response)
        obj.raw = CachedHTTPResponse.from_response(response)
        obj.request = CachedRequest.from_request(response.request)
        obj._next = CachedRequest.from_request(response.next) if response.next else None

        # Store response body, which will have been read & decoded by requests.Response by now
        obj._content = response.content

        obj._convert_redirects()
        return obj

    def _convert_redirects(self):
        """Convert redirect history, if any; avoid recursion by not copying redirects of redirects"""
        if self.is_redirect:
            self.history = []
            return
        self.history = [self.from_response(redirect) for redirect in self.history]

    @property
    def _content_consumed(self) -> bool:
        """For compatibility with requests.Response; will always be True for a cached response"""
        return True

    @_content_consumed.setter
    def _content_consumed(self, value: bool):
        pass

    @property
    def expires_delta(self) -> Optional[int]:
        """Get time to expiration in seconds (rounded to the nearest second)"""
        if self.expires is None:
            return None
        delta = self.expires - utcnow()
        return round(delta.total_seconds())

    @property
    def expires_unix(self) -> Optional[int]:
        """Get expiration time as a Unix timestamp"""
        if self.expires is None:
            return None
        return round(self.expires.timestamp())

    @property
    def from_cache(self) -> bool:
        return True

    @property
    def is_expired(self) -> bool:
        """Determine if this cached response is expired"""
        return self.expires is not None and utcnow() >= self.expires

    def is_older_than(self, older_than: ExpirationTime) -> bool:
        """Determine if this cached response is older than the given time"""
        older_than = get_expiration_datetime(older_than, negative_delta=True)
        return older_than is not None and self.created_at < older_than

    @property
    def next(self) -> Optional[PreparedRequest]:
        """Returns a PreparedRequest for the next request in a redirect chain, if there is one."""
        return self._next.prepare() if self._next else None

    def reset_expiration(self, expire_after: ExpirationTime):
        """Set a new expiration for this response"""
        self.expires = get_expiration_datetime(expire_after)
        return self.is_expired

    @property
    def size(self) -> int:
        """Get the size of the response body in bytes"""
        return len(self.content) if self.content else 0

    def __getstate__(self):
        """Override pickling behavior from ``requests.Response.__getstate__``"""
        return self.__dict__

    def __setstate__(self, state):
        """Override pickling behavior from ``requests.Response.__setstate__``"""
        for name, value in state.items():
            setattr(self, name, value)

    def __str__(self):
        return (
            f'<CachedResponse [{self.status_code}]: "'
            f"created: {format_datetime(self.created_at)}, "
            f'expires: {format_datetime(self.expires)} ({"stale" if self.is_expired else "fresh"}), '
            f"size: {format_file_size(self.size)}, request: {self.request}>"
        )


def format_datetime(value: Optional[datetime]) -> str:
    """Get a formatted datetime string in the local time zone"""
    if not value:
        return 'N/A'
    return value.astimezone().strftime(DATETIME_FORMAT)


def format_file_size(n_bytes: int) -> str:
    """Convert a file size in bytes into a human-readable format"""
    filesize = float(n_bytes or 0)

    def _format(unit):
        return f'{int(filesize)} {unit}' if unit == 'bytes' else f'{filesize:.2f} {unit}'

    for unit in ['bytes', 'KiB', 'MiB', 'GiB']:
        if filesize < 1024 or unit == 'GiB':
            return _format(unit)
        filesize /= 1024

    if TYPE_CHECKING:
        return _format(unit)
