"""Main classes to add caching features to :py:class:`requests.Session`"""

from contextlib import contextmanager, nullcontext
from logging import getLogger
from threading import RLock, Thread
from typing import TYPE_CHECKING, Iterable, MutableMapping, Optional, Union

from requests import PreparedRequest
from requests import Session as OriginalSession
from requests.hooks import dispatch_hook

from ._utils import get_valid_kwargs, patch_form_boundary
from .backends import BackendSpecifier, StrOrPath, init_backend
from .models import AnyResponse, CachedResponse, OriginalResponse
from .policy import (
    DEFAULT_CACHE_NAME,
    DEFAULT_IGNORED_PARAMS,
    DEFAULT_METHODS,
    DEFAULT_STATUS_CODES,
    CacheActions,
    CacheSettings,
    ExpirationPatterns,
    ExpirationTime,
    FilterCallback,
    KeyCallback,
    set_request_headers,
)
from .serializers import SerializerType

__all__ = ['CachedSession', 'CacheMixin']
if TYPE_CHECKING:
    MIXIN_BASE = OriginalSession
else:
    MIXIN_BASE = object

logger = getLogger(__name__)


class CacheMixin(MIXIN_BASE):
    """Mixin class that extends :py:class:`requests.Session` with caching features.
    See :py:class:`.CachedSession` for usage details.
    """

    def __init__(
        self,
        cache_name: StrOrPath = DEFAULT_CACHE_NAME,
        backend: Optional[BackendSpecifier] = None,
        serializer: Optional[SerializerType] = None,
        expire_after: ExpirationTime = -1,
        urls_expire_after: Optional[ExpirationPatterns] = None,
        cache_control: bool = False,
        allowable_codes: Iterable[int] = DEFAULT_STATUS_CODES,
        allowable_methods: Iterable[str] = DEFAULT_METHODS,
        always_revalidate: bool = False,
        ignored_parameters: Iterable[str] = DEFAULT_IGNORED_PARAMS,
        match_headers: Union[Iterable[str], bool] = False,
        filter_fn: Optional[FilterCallback] = None,
        key_fn: Optional[KeyCallback] = None,
        stale_if_error: Union[bool, int] = False,
        **kwargs,
    ):
        self.cache = init_backend(cache_name, backend, serializer=serializer, **kwargs)
        self.settings = CacheSettings.from_kwargs(
            expire_after=expire_after,
            urls_expire_after=urls_expire_after,
            cache_control=cache_control,
            allowable_codes=allowable_codes,
            allowable_methods=allowable_methods,
            always_revalidate=always_revalidate,
            ignored_parameters=ignored_parameters,
            match_headers=match_headers,
            filter_fn=filter_fn,
            key_fn=key_fn,
            stale_if_error=stale_if_error,
            **kwargs,
        )
        self._lock = RLock()

        # If the mixin superclass is a custom Session, pass along any valid kwargs
        super().__init__(**get_valid_kwargs(super().__init__, kwargs))

    @classmethod
    def wrap(cls, original_session: OriginalSession, **kwargs) -> 'CacheMixin':
        """Add caching to an existing :py:class:`~requests.Session` object, while retaining all
        original session settings.

        Args:
            original_session: Session object to wrap
            kwargs: Keyword arguments for :py:class:`.CachedSession`
        """
        session = cls(**kwargs)
        session.adapters = original_session.adapters
        session.auth = original_session.auth
        session.cert = original_session.cert
        session.cookies = original_session.cookies
        session.headers = original_session.headers
        session.hooks = original_session.hooks
        session.max_redirects = original_session.max_redirects
        session.params = original_session.params
        session.proxies = original_session.proxies
        session.stream = original_session.stream
        session.trust_env = original_session.trust_env
        session.verify = original_session.verify
        return session

    @property
    def settings(self) -> CacheSettings:
        """Settings that affect cache behavior"""
        return self.cache._settings

    @settings.setter
    def settings(self, value: CacheSettings):
        self.cache._settings = value

    # For backwards-compatibility
    @property
    def expire_after(self) -> ExpirationTime:
        return self.settings.expire_after

    @expire_after.setter
    def expire_after(self, value: ExpirationTime):
        self.settings.expire_after = value

    # Wrapper methods to add return type hints
    def get(self, url: str, params=None, **kwargs) -> AnyResponse:  # type: ignore
        kwargs.setdefault('allow_redirects', True)
        return self.request('GET', url, params=params, **kwargs)

    def options(self, url: str, **kwargs) -> AnyResponse:  # type: ignore
        kwargs.setdefault('allow_redirects', True)
        return self.request('OPTIONS', url, **kwargs)

    def head(self, url: str, **kwargs) -> AnyResponse:  # type: ignore
        kwargs.setdefault('allow_redirects', False)
        return self.request('HEAD', url, **kwargs)

    def post(self, url: str, data=None, **kwargs) -> AnyResponse:  # type: ignore
        return self.request('POST', url, data=data, **kwargs)

    def put(self, url: str, data=None, **kwargs) -> AnyResponse:  # type: ignore
        return self.request('PUT', url, data=data, **kwargs)

    def patch(self, url: str, data=None, **kwargs) -> AnyResponse:  # type: ignore
        return self.request('PATCH', url, data=data, **kwargs)

    def delete(self, url: str, **kwargs) -> AnyResponse:  # type: ignore
        return self.request('DELETE', url, **kwargs)

    def request(  # type: ignore
        self,
        method: str,
        url: str,
        *args,
        headers: Optional[MutableMapping[str, str]] = None,
        expire_after: ExpirationTime = None,
        only_if_cached: bool = False,
        refresh: bool = False,
        force_refresh: bool = False,
        **kwargs,
    ) -> AnyResponse:
        """This method prepares and sends a request while automatically performing any necessary
        caching operations. This will be called by any other method-specific ``requests`` functions
        (get, post, etc.). This is not used by :py:class:`~requests.PreparedRequest` objects, which
        are handled by :py:meth:`send()`.

        See :py:meth:`requests.Session.request` for base parameters. Additional parameters:

        Args:
            expire_after: Expiration time to set only for this request. See :ref:`expiration` for
                details.
            only_if_cached: Only return results from the cache. If not cached, return a 504 response
                instead of sending a new request.
            refresh: Revalidate with the server before using a cached response, and refresh if needed
                (e.g., a "soft refresh," like F5 in a browser)
            force_refresh: Always make a new request, and overwrite any previously cached response
                (e.g., a "hard refresh", like Ctrl-F5 in a browser))

        Returns:
            Either a new or cached response
        """
        headers = set_request_headers(headers, expire_after, only_if_cached, refresh, force_refresh)
        with patch_form_boundary() if kwargs.get('files') else nullcontext():
            return super().request(method, url, *args, headers=headers, **kwargs)  # type: ignore

    def send(
        self,
        request: PreparedRequest,
        expire_after: ExpirationTime = None,
        only_if_cached: bool = False,
        refresh: bool = False,
        force_refresh: bool = False,
        **kwargs,
    ) -> AnyResponse:
        """Send a prepared request, with caching. See :py:meth:`requests.Session.send` for base
        parameters, and see :py:meth:`.request` for extra parameters.

        **Order of operations:** For reference, a request will pass through the following methods:

        1. :py:func:`requests.get`, :py:meth:`CachedSession.get`, etc. (optional)
        2. :py:meth:`.CachedSession.request`
        3. :py:meth:`requests.Session.request`
        4. :py:meth:`.CachedSession.send`
        5. :py:meth:`.BaseCache.get_response`
        6. :py:meth:`requests.Session.send` (if not using a cached response)
        7. :py:meth:`.BaseCache.save_response` (if not using a cached response)
        """
        # Determine which actions to take based on settings and request info
        request.headers = set_request_headers(
            request.headers, expire_after, only_if_cached, refresh, force_refresh
        )
        actions = CacheActions.from_request(
            self.cache.create_key(request, **kwargs), request, self.settings
        )

        # Attempt to fetch a cached response
        cached_response: Optional[CachedResponse] = None
        if not actions.skip_read:
            cached_response = self.cache.get_response(actions.cache_key)
        actions.update_from_cached_response(cached_response, self.cache.create_key, **kwargs)

        # Handle missing and expired responses based on settings and headers
        if actions.error_504:
            response: AnyResponse = get_504_response(request)
        elif actions.resend_async:
            self._resend_async(request, actions, cached_response, **kwargs)
            response = cached_response  # type: ignore
        elif actions.resend_request:
            response = self._resend(request, actions, cached_response, **kwargs)  # type: ignore
        elif actions.send_request:
            response = self._send_and_cache(request, actions, cached_response, **kwargs)
        else:
            response = cached_response  # type: ignore  # Guaranteed to be non-None by this point

        # If the request has been filtered out and was previously cached, delete it
        if self.settings.filter_fn is not None and not self.settings.filter_fn(response):
            logger.debug(f'Deleting filtered response for URL: {response.url}')
            self.cache.delete(actions.cache_key)
            return response

        # Dispatch any hooks here, because they are removed during serialization
        return dispatch_hook('response', request.hooks, response, **kwargs)

    def _send_and_cache(
        self,
        request: PreparedRequest,
        actions: CacheActions,
        cached_response: Optional[CachedResponse] = None,
        **kwargs,
    ) -> AnyResponse:
        """Send a request and cache the response, unless disabled by settings or headers.
        If applicable, also handle conditional requests.
        """
        request = actions.update_request(request)
        response = super().send(request, **kwargs)
        actions.update_from_response(response)

        if not actions.skip_write:
            self.cache.save_response(response, actions.cache_key, actions.expires)
        elif cached_response is not None and response.status_code == 304:
            cached_response = actions.update_revalidated_response(response, cached_response)
            if not actions.skip_write:
                self.cache.save_response(cached_response, actions.cache_key, actions.expires)  # type: ignore[unreachable]
            return cached_response
        else:
            logger.debug(f'Skipping cache write for URL: {request.url}')

        # This is possible if the original request is a cache miss, but updating its validation
        # headers results in redirecting to a different URL that is a cache hit
        if isinstance(response, CachedResponse):
            return response
        else:
            return OriginalResponse.wrap_response(response, actions)

    def _resend(
        self,
        request: PreparedRequest,
        actions: CacheActions,
        cached_response: CachedResponse,
        **kwargs,
    ) -> AnyResponse:
        """Handle a stale cached response by attempting to resend the request and cache a fresh
        response
        """
        logger.debug('Stale response; attempting to re-send request')
        try:
            response = self._send_and_cache(request, actions, cached_response, **kwargs)
            if (
                self.settings.stale_if_error
                and response.status_code not in self.settings.allowable_codes
            ):
                response.raise_for_status()
            return response
        except Exception:
            return self._handle_error(cached_response, actions)

    def _resend_async(self, *args, **kwargs):
        """Send a non-blocking request to refresh a cached response"""
        logger.debug('Using stale response while revalidating')
        thread = Thread(target=self._send_and_cache, args=args, kwargs=kwargs)
        thread.start()

    def _handle_error(self, cached_response: CachedResponse, actions: CacheActions) -> AnyResponse:
        """Handle a request error based on settings:
        * Default behavior: re-raise the error
        * stale-if-error: Ignore the error and and return the stale cache item
        """
        if actions.is_usable(cached_response, error=True):
            logger.warning(
                f'Request for URL {cached_response.request.url} failed; using cached response',
                exc_info=True,
            )
            return cached_response
        else:
            raise

    @contextmanager
    def cache_disabled(self):
        """
        Context manager for temporary disabling the cache

        .. warning:: This method is not thread-safe.

        Example:

            >>> s = CachedSession()
            >>> with s.cache_disabled():
            ...     s.get('https://httpbin.org/ip')

        """
        if self.settings.disabled:
            yield
        else:
            self.settings.disabled = True
            try:
                yield
            finally:
                self.settings.disabled = False

    def close(self):
        """Close the session and any open backend connections"""
        super().close()
        self.cache.close()

    def __getstate__(self):
        # Unlike requests.Session, CachedSession may contain backend connection objects that can't
        # be pickled. Support for this could be added if necessary, but for now it's explicitly
        # disabled to avoid confusing errors upon unpickling.
        raise NotImplementedError('CachedSession cannot be pickled')

    def __repr__(self):
        return f'<CachedSession(cache={repr(self.cache)}, settings={self.settings})>'


class CachedSession(CacheMixin, OriginalSession):
    """Session class that extends :py:class:`requests.Session` with caching features.

    See individual :py:mod:`backend classes <requests_cache.backends>` for additional
    backend-specific arguments. Also see :ref:`user-guide` for more details and examples on how the
    following arguments affect cache behavior.

    Args:
        cache_name: Used as a cache path, prefix, or namespace, depending on the backend
        backend: Cache backend name or instance; name may be one of
            ``['sqlite', 'filesystem', 'mongodb', 'gridfs', 'redis', 'dynamodb', 'memory']``
        serializer: Serializer name or instance; name may be one of
            ``['pickle', 'json', 'yaml', 'bson']``.
        expire_after: Time after which cached items will expire. See :ref:`expiration` for details.
        urls_expire_after: Expiration times to apply for different URL patterns
        cache_control: Use Cache-Control and other response headers to set expiration
        allowable_codes: Only cache responses with one of these status codes
        allowable_methods: Cache only responses for one of these HTTP methods
        always_revalidate: Revalidate with the server for every request, even if the cached response
            is not expired
        match_headers: Request headers to match, when `Vary` response header is not available. May
            be a list of headers, or ``True`` to match all.
        ignored_parameters: Request parameters, headers, and/or JSON body params to exclude from both
            request matching and cached request data
        stale_if_error: Return a stale response if a new request raises an exception. Optionally
            accepts a time value representing maximum staleness to accept.
        stale_while_revalidate: Return a stale response initially, while a non-blocking request is
            sent to refresh the response for the next time it's requested
        filter_fn: Response filtering function that indicates whether or not a given response should
            be cached. See :ref:`custom-filtering` for details.
        key_fn: Request matching function for generating custom cache keys. See
            :ref:`custom-matching` for details.
    """


def get_504_response(request: PreparedRequest) -> CachedResponse:
    """Get a 504: Not Cached error response, for use with only-if-cached option"""
    return CachedResponse(
        url=request.url or '',
        status_code=504,
        reason='Not Cached',
        request=request,  # type: ignore
    )
