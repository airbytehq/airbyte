"""Utility functions for parsing and converting expiration values"""

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from fnmatch import fnmatch
from logging import getLogger
from math import ceil
from typing import Optional
from typing import Pattern as RegexPattern

from .._utils import try_int
from . import ExpirationPattern, ExpirationPatterns, ExpirationTime

# Special expiration values that may be set by either headers or keyword args
DO_NOT_CACHE = 0x0D0E0200020704  # Per RFC 4824
EXPIRE_IMMEDIATELY = 0
NEVER_EXPIRE = -1

logger = getLogger(__name__)


def get_expiration_datetime(
    expire_after: ExpirationTime,
    start_time: Optional[datetime] = None,
    negative_delta: bool = False,
    ignore_invalid_httpdate: bool = False,
) -> Optional[datetime]:
    """Convert an expiration value in any supported format to an absolute datetime"""
    # Never expire (or do not cache, in which case expiration won't be used)
    if expire_after is None or expire_after in [NEVER_EXPIRE, DO_NOT_CACHE]:
        return None
    # Expire immediately
    elif try_int(expire_after) == EXPIRE_IMMEDIATELY:
        return start_time or utcnow()
    # Already a datetime or httpdate str (allowed for headers only)
    if isinstance(expire_after, str):
        expire_after_dt = _parse_http_date(expire_after)
        if not expire_after_dt and not ignore_invalid_httpdate:
            raise ValueError(f'Invalid HTTP date: {expire_after}')
        return expire_after_dt
    elif isinstance(expire_after, datetime):
        return expire_after.astimezone(timezone.utc)

    # Otherwise, it must be a timedelta or time in seconds
    if not isinstance(expire_after, timedelta):
        expire_after = timedelta(seconds=expire_after)
    if negative_delta:
        expire_after = -expire_after
    return (start_time or utcnow()) + expire_after


def get_expiration_seconds(expire_after: ExpirationTime) -> int:
    """Convert an expiration value in any supported format to an expiration time in seconds"""
    if expire_after == DO_NOT_CACHE:
        return DO_NOT_CACHE
    expires = get_expiration_datetime(expire_after, ignore_invalid_httpdate=True)
    return ceil((expires - utcnow()).total_seconds()) if expires else NEVER_EXPIRE


def get_url_expiration(
    url: Optional[str], urls_expire_after: Optional[ExpirationPatterns] = None
) -> ExpirationTime:
    """Check for a matching per-URL expiration, if any"""
    if not url:
        return None

    for pattern, expire_after in (urls_expire_after or {}).items():
        if _url_match(url, pattern):
            logger.debug(f'URL {url} matched pattern "{pattern}": {expire_after}')
            return expire_after
    return None


def add_tzinfo(dt: Optional[datetime]) -> Optional[datetime]:
    """Add a UTC timezone to a datetime object, if it doesn't already have one. This is used mainly
    during deserialization for backends that don't store timezone info.
    """
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def utcnow() -> datetime:
    """Get the current time in UTC (timezone-aware)"""
    return datetime.now(timezone.utc)


def _parse_http_date(value: str) -> Optional[datetime]:
    """Attempt to parse an HTTP (RFC 5322-compatible) timestamp"""
    try:
        expire_after = parsedate_to_datetime(value)
        return expire_after.astimezone(timezone.utc)
    except (TypeError, ValueError):
        logger.debug(f'Failed to parse timestamp: {value}')
        return None


def _url_match(url: str, pattern: ExpirationPattern) -> bool:
    """Determine if a URL matches a pattern

    Args:
        url: URL to test. Its base URL (without protocol) will be used.
        pattern: Glob pattern to match against. A recursive wildcard will be added if not present

    Example:
        >>> url_match('https://httpbin.org/delay/1', 'httpbin.org/delay')
        True
        >>> url_match('https://httpbin.org/stream/1', 'httpbin.org/*/1')
        True
        >>> url_match('https://httpbin.org/stream/2', 'httpbin.org/*/1')
        False
        >>> url_match('https://httpbin.org/stream/2', re.compile('httpbin.org/*/\\d+'))
        True
        >>> url_match('https://httpbin.org/stream/x', re.compile('httpbin.org/*/\\d+'))
        False
    """
    if isinstance(pattern, RegexPattern):
        match = pattern.search(url)
        return match is not None
    else:
        url = url.split('://')[-1]
        pattern = pattern.split('://')[-1].rstrip('*') + '**'
        return fnmatch(url, pattern)
