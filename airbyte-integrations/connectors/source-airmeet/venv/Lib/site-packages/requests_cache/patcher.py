"""Utilities for patching ``requests``. See :ref:`patching` for general usage info.

.. warning::
    These functions are not thread-safe. Use :py:class:`.CachedSession` if you want to use caching
    in a multi-threaded environment.

.. automodsumm:: requests_cache.patcher
   :functions-only:
   :nosignatures:
"""

from contextlib import contextmanager
from logging import getLogger
from typing import Optional, Type

import requests

from .backends import BackendSpecifier, BaseCache, init_backend
from .session import CachedSession, OriginalSession

logger = getLogger(__name__)


def install_cache(
    cache_name: str = 'http_cache',
    backend: Optional[BackendSpecifier] = None,
    session_factory: Type[OriginalSession] = CachedSession,
    **kwargs,
):
    """
    Install the cache for all ``requests`` functions by monkey-patching :py:class:`requests.Session`

    Example:

        >>> requests_cache.install_cache('demo_cache')

    Accepts all the same parameters as :py:class:`.CachedSession`. Additional parameters:

    Args:
        session_factory: Session class to use. It must inherit from either
            :py:class:`.CachedSession` or :py:class:`.CacheMixin`
    """
    backend = init_backend(cache_name, backend, **kwargs)

    class _ConfiguredCachedSession(session_factory):  # type: ignore  # See mypy issue #5865
        def __init__(self):
            super().__init__(cache_name=cache_name, backend=backend, **kwargs)

    _patch_session_factory(_ConfiguredCachedSession)


def uninstall_cache():
    """Disable the cache by restoring the original :py:class:`requests.Session`"""
    _patch_session_factory(OriginalSession)


@contextmanager
def disabled():
    """
    Context manager for temporarily disabling caching for all ``requests`` functions

    Example:

        >>> with requests_cache.disabled():
        ...     requests.get('https://httpbin.org/get')

    """
    previous = requests.Session
    uninstall_cache()
    try:
        yield
    finally:
        _patch_session_factory(previous)


@contextmanager
def enabled(*args, **kwargs):
    """
    Context manager for temporarily enabling caching for all ``requests`` functions

    Example:

        >>> with requests_cache.enabled('cache.db'):
        ...     requests.get('https://httpbin.org/get')

    Accepts the same arguments as :py:class:`.CachedSession` and :py:func:`.install_cache`.
    """
    install_cache(*args, **kwargs)
    try:
        yield
    finally:
        uninstall_cache()


def get_cache() -> Optional[BaseCache]:
    """Get the internal cache object from the currently installed ``CachedSession`` (if any)"""
    return getattr(requests.Session(), 'cache', None)


def is_installed() -> bool:
    """Indicate whether or not requests-cache is currently installed"""
    return isinstance(requests.Session(), CachedSession)


def clear():
    """Clear the currently installed cache (if any)"""
    if get_cache():
        get_cache().clear()


def delete(*args, **kwargs):
    """Remove responses from the cache according one or more conditions.
    See :py:meth:`.BaseCache.delete` for usage details.
    """
    session = requests.Session()
    if isinstance(session, CachedSession):
        session.cache.delete(*args, **kwargs)


def _patch_session_factory(session_factory: Type[OriginalSession] = CachedSession):
    logger.debug(f'Patching requests.Session with class: {session_factory.__name__}')
    requests.Session = requests.sessions.Session = session_factory  # type: ignore
