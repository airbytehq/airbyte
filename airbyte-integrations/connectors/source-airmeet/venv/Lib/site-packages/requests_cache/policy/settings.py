from typing import Dict, Iterable, Union

from attrs import define, field

from .._utils import get_valid_kwargs
from ..models import RichMixin
from . import ExpirationPattern, ExpirationTime, FilterCallback, KeyCallback

ALL_METHODS = ('GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE')
DEFAULT_CACHE_NAME = 'http_cache'
DEFAULT_METHODS = ('GET', 'HEAD')
DEFAULT_STATUS_CODES = (200,)

# Default params and/or headers that are excluded from cache keys and redacted from cached responses
DEFAULT_IGNORED_PARAMS = ('Authorization', 'X-API-KEY', 'access_token', 'api_key')


@define(repr=False)
class CacheSettings(RichMixin):
    """Class used internally to store settings that affect caching behavior. This allows settings
    to be used across multiple modules, but exposed to the user in a single property
    (:py:attr:`.CachedSession.settings`). These values can safely be modified after initialization.
    See :py:class:`.CachedSession` and :ref:`user-guide` for usage details.
    """

    allowable_codes: Iterable[int] = field(default=DEFAULT_STATUS_CODES)
    allowable_methods: Iterable[str] = field(default=DEFAULT_METHODS)
    always_revalidate: bool = field(default=False)
    cache_control: bool = field(default=False)
    disabled: bool = field(default=False)
    expire_after: ExpirationTime = field(default=None)
    filter_fn: FilterCallback = field(default=None)
    ignored_parameters: Iterable[str] = field(default=DEFAULT_IGNORED_PARAMS)
    key_fn: KeyCallback = field(default=None)
    match_headers: Union[Iterable[str], bool] = field(default=False)
    only_if_cached: bool = field(default=False)
    stale_if_error: Union[bool, ExpirationTime] = field(default=False)
    stale_while_revalidate: Union[bool, ExpirationTime] = field(default=False)
    urls_expire_after: Dict[ExpirationPattern, ExpirationTime] = field(factory=dict)

    @classmethod
    def from_kwargs(cls, **kwargs):
        """Constructor with some additional steps:

        * Handle some deprecated argument names
        * Ignore invalid settings, for easier initialization from mixed ``**kwargs``
        """
        kwargs = cls._rename_kwargs(kwargs)
        kwargs = get_valid_kwargs(cls.__init__, kwargs)
        return cls(**kwargs)

    @staticmethod
    def _rename_kwargs(kwargs):
        if 'old_data_on_error' in kwargs:
            kwargs['stale_if_error'] = kwargs.pop('old_data_on_error')
        if 'include_get_headers' in kwargs:
            kwargs['match_headers'] = kwargs.pop('include_get_headers')
        return kwargs
