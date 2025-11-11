from io import BytesIO
from logging import getLogger
from typing import TYPE_CHECKING, Optional

from attrs import define, field, fields_dict
from requests import Response
from urllib3.response import (  # type: ignore  # import location false positive
    HTTPHeaderDict,
    HTTPResponse,
    is_fp_closed,
)

from . import RichMixin

logger = getLogger(__name__)


if TYPE_CHECKING:
    from . import CachedResponse


@define(auto_attribs=False, repr=False, slots=False)
class CachedHTTPResponse(RichMixin, HTTPResponse):
    """A wrapper class that emulates :py:class:`~urllib3.response.HTTPResponse`.

    This enables consistent behavior for streaming requests and generator usage in the following
    cases:
    * On an original response, after reading its content to write to the cache
    * On a cached response
    """

    decode_content: bool = field(default=None)
    headers: HTTPHeaderDict = field(factory=HTTPHeaderDict)
    reason: str = field(default=None)
    request_url: str = field(default=None)
    status: int = field(default=0)
    version: int = field(default=0)

    def __init__(self, body: Optional[bytes] = None, **kwargs):
        """First initialize via HTTPResponse.__init__, then via __attrs_init__"""
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(body=BytesIO(body or b''), preload_content=False, **kwargs)
        self._body = body
        self._fp_bytes_read = 0
        self.length_remaining = len(body or b'')
        self.__attrs_init__(**kwargs)  # type: ignore # False positive in mypy 0.920+?

    @classmethod
    def from_response(cls, response: Response) -> 'CachedHTTPResponse':
        """Create a CachedHTTPResponse based on an original response, and restore the response to
        its previous state.
        """
        # Get basic attributes
        kwargs = {k: getattr(response.raw, k, None) for k in fields_dict(cls).keys()}
        # Init kwarg for HTTPResponse._request_url has no leading '_'
        kwargs['request_url'] = response.raw._request_url
        kwargs['body'] = _copy_body(response)
        return cls(**kwargs)  # type: ignore  # False positive in mypy 0.920+?

    @classmethod
    def from_cached_response(cls, response: 'CachedResponse'):
        """Create a CachedHTTPResponse based on a cached response"""
        obj = cls(
            headers=HTTPHeaderDict(response.headers),
            reason=response.reason,
            status=response.status_code,
            request_url=response.request.url,
        )
        obj.reset(response._content)
        return obj

    @property
    def _request_url(self) -> str:
        """For compatibility with urllib3"""
        return self.request_url

    @_request_url.setter
    def _request_url(self, value: str):
        self.request_url = value

    def release_conn(self):
        """No-op for compatibility"""

    def read(self, amt=None, decode_content=None, **kwargs):
        """Simplified reader for cached content that emulates
        :py:meth:`urllib3.response.HTTPResponse.read()`, but does not need to read from a socket
        or decode content.
        """
        if 'Content-Encoding' in self.headers and decode_content is False:
            logger.warning('read(decode_content=False) is not supported for cached responses')
        if is_fp_closed(self._fp):
            return b''

        data = self._fp.read(amt)
        if data:
            self._fp_bytes_read += len(data)
            if self.length_remaining is not None:
                self.length_remaining -= len(data)
        # "close" the file to inform consumers to stop reading from it
        else:
            self._fp.close()
        return data

    def reset(self, body: Optional[bytes] = None):
        """Reset raw response file pointer, and optionally update content"""
        _reset_fp(self, body or self._body)

    def stream(self, amt=None, **kwargs):
        """Simplified generator over cached content that emulates
        :py:meth:`urllib3.response.HTTPResponse.stream()`
        """
        while not self._fp.closed:
            yield self.read(amt=amt, **kwargs)


def _copy_body(response: Response) -> Optional[bytes]:
    """Read and copy raw response data, and then restore response object to its previous state.
    This is necessary so streaming responses behave consistently with or without the cache.
    """
    # File pointer is missing or closed; nothing to do
    if not getattr(response.raw, '_fp', None) or is_fp_closed(response.raw._fp):
        return None
    # Body has already been read & decoded by requests
    elif getattr(response.raw, '_has_decoded_content', False):
        body = response.content
    # Body has not yet been read
    else:
        body = response.raw.read(decode_content=False)
        _reset_fp(response.raw, body)
        _ = response.content  # This property reads, decodes, and stores response content

    # After reading, reset file pointer once more so client can still read it as a stream
    _reset_fp(response.raw, body)
    return body


def _reset_fp(raw: HTTPResponse, body: Optional[bytes] = None):
    """Set content and reset raw response file pointer"""
    body = body or b''
    raw._body = body  # type: ignore[attr-defined]
    raw._fp_bytes_read = 0  # type: ignore[attr-defined]
    raw._fp = BytesIO(body)  # type: ignore[attr-defined]
    raw.length_remaining = len(body)
