from logging import getLogger
from urllib.parse import urlsplit

from attrs import asdict, define, field, fields_dict
from requests import PreparedRequest
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict

from ..cache_keys import encode
from . import RichMixin

logger = getLogger(__name__)


@define(repr=False)
class CachedRequest(RichMixin):
    """A serializable dataclass that emulates :py:class:`requests.PreparedResponse`"""

    body: bytes = field(default=None, converter=encode)
    cookies: RequestsCookieJar = field(factory=RequestsCookieJar)
    headers: CaseInsensitiveDict = field(factory=CaseInsensitiveDict)
    method: str = field(default=None)
    url: str = field(default=None)

    @classmethod
    def from_request(cls, original_request: PreparedRequest) -> 'CachedRequest':
        """Create a CachedRequest based on an original request object"""
        kwargs = {k: getattr(original_request, k, None) for k in fields_dict(cls).keys()}
        kwargs['cookies'] = getattr(original_request, '_cookies', None)
        return cls(**kwargs)  # type: ignore  # False positive in mypy 0.920+?

    @property
    def path_url(self):
        p = urlsplit(self.url)
        url = p.path or '/'
        url += f'?{p.query}' if p.query else ''
        return url

    def copy(self) -> 'CachedRequest':
        """Return a copy of the CachedRequest"""
        return self.__class__(**asdict(self))

    def prepare(self) -> PreparedRequest:
        """Convert the CachedRequest back into a PreparedRequest"""
        prepared_request = PreparedRequest()
        prepared_request.prepare(
            cookies=self.cookies,
            data=self.body,
            headers=self.headers,
            method=self.method,
            url=self.url,
        )
        return prepared_request

    @property
    def _cookies(self):
        """For compatibility with PreparedRequest, which has an attribute named '_cookies', and a
        keyword argument named 'cookies'.
        """
        return self.cookies

    def __str__(self):
        return f'{self.method} {self.url}'
