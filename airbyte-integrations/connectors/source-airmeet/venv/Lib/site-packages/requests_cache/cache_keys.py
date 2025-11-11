"""Internal utilities for generating cache keys that are used for request matching

.. automodsumm:: requests_cache.cache_keys
   :functions-only:
   :nosignatures:
"""

from __future__ import annotations

import json
from contextlib import nullcontext
from hashlib import blake2b
from logging import getLogger
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from requests import Request, Session
from requests.structures import CaseInsensitiveDict
from url_normalize import url_normalize

from ._utils import decode, encode, patch_form_boundary, is_json_content_type

__all__ = [
    'create_key',
    'normalize_body',
    'normalize_headers',
    'normalize_request',
    'normalize_params',
    'normalize_url',
]
if TYPE_CHECKING:
    from .models import AnyPreparedRequest, AnyRequest, CachedResponse

# Maximum JSON request body size that will be filtered and normalized
MAX_NORM_BODY_SIZE = 10 * 1024 * 1024

KVList = List[Tuple[str, str]]
ParamList = Optional[Iterable[str]]
RequestContent = Union[Mapping, str, bytes]

logger = getLogger(__name__)


def create_key(
    request: AnyRequest,
    ignored_parameters: ParamList = None,
    match_headers: Union[ParamList, bool] = False,
    serializer: Any = None,
    **request_kwargs,
) -> str:
    """Create a normalized cache key based on a request object

    Args:
        request: Request object to generate a cache key from
        ignored_parameters: Request parameters, headers, and/or JSON body params to exclude
        match_headers: Match only the specified headers, or ``True`` to match all headers
        request_kwargs: Additional keyword arguments for :py:func:`~requests.request`
    """
    # Normalize and gather all relevant request info to match against
    request = normalize_request(request, ignored_parameters)
    key_parts = [
        request.method or '',
        request.url,
        request.body or '',
        bool(request_kwargs.get('verify', True)),
        *get_matched_headers(request.headers, match_headers),
        str(serializer),
    ]

    # Generate a hash based on this info
    key = blake2b(digest_size=8)
    for part in key_parts:
        key.update(encode(part))
    return key.hexdigest()


def get_matched_headers(
    headers: CaseInsensitiveDict, match_headers: Union[ParamList, bool]
) -> List[str]:
    """Get only the headers we should match against as a list of ``k=v`` strings, given an optional
    include list.
    """
    if not match_headers:
        return []
    if match_headers is True:
        match_headers = headers
    return [
        f'{k.lower()}={headers[k]}'
        for k in sorted(match_headers, key=lambda x: x.lower())
        if k in headers
    ]


def normalize_request(
    request: AnyRequest, ignored_parameters: ParamList = None
) -> AnyPreparedRequest:
    """Normalize and remove ignored parameters from request URL, body, and headers.
    This is used for both:

    * Increasing cache hits by generating more precise cache keys
    * Redacting potentially sensitive info from cached requests

    Args:
        request: Request object to normalize
        ignored_parameters: Request parameters, headers, and/or JSON body params to exclude
    """
    if isinstance(request, Request):
        # For a multipart POST request that hasn't been prepared, we need to patch the form boundary
        # so the request body will have a consistent hash
        with patch_form_boundary() if request.files else nullcontext():
            norm_request: AnyPreparedRequest = Session().prepare_request(request)
    else:
        norm_request = request.copy()

    norm_request.method = (norm_request.method or '').upper()
    norm_request.url = normalize_url(norm_request.url or '', ignored_parameters)
    norm_request.headers = normalize_headers(norm_request.headers, ignored_parameters)
    norm_request.body = normalize_body(norm_request, ignored_parameters)
    return norm_request


def normalize_headers(
    headers: MutableMapping[str, str], ignored_parameters: ParamList = None
) -> CaseInsensitiveDict:
    """Sort and filter request headers, and normalize minor variations in multi-value headers"""
    headers = {k: decode(v) for (k, v) in headers.items()}
    if ignored_parameters:
        headers = filter_sort_dict(headers, ignored_parameters)
    for k, v in headers.items():
        if ',' in v:
            values = [v.strip() for v in v.lower().split(',') if v.strip()]
            headers[k] = ', '.join(sorted(values))
    return CaseInsensitiveDict(headers)


def normalize_url(url: str, ignored_parameters: ParamList) -> str:
    """Normalize and filter a URL. This includes request parameters, IDN domains, scheme, host,
    port, etc.
    """
    url = filter_url(url, ignored_parameters)
    return url_normalize(url)


def normalize_body(request: AnyPreparedRequest, ignored_parameters: ParamList) -> bytes:
    """Normalize and filter a request body if possible, depending on Content-Type"""
    if not request.body:
        return b''

    filtered_body: Union[str, bytes] = request.body
    try:
        content_type = request.headers['Content-Type'].split(';')[0].lower()
    except (AttributeError, KeyError):
        content_type = ''

    # Filter and sort params if possible
    if is_json_content_type(content_type):
        filtered_body = normalize_json_body(request.body, ignored_parameters)
    elif content_type == 'application/x-www-form-urlencoded':
        filtered_body = normalize_params(request.body, ignored_parameters)

    return encode(filtered_body)


def normalize_json_body(
    original_body: Union[str, bytes], ignored_parameters: ParamList
) -> Union[str, bytes]:
    """Normalize and filter a request body with serialized JSON data"""
    if len(original_body) <= 2 or len(original_body) > MAX_NORM_BODY_SIZE:
        return original_body

    try:
        body = json.loads(decode(original_body))
        body = filter_sort_json(body, ignored_parameters)
        return json.dumps(body)
    # If it's invalid JSON, then don't mess with it
    except (AttributeError, TypeError, ValueError):
        logger.debug('Invalid JSON body')
        return original_body


def normalize_params(value: Union[str, bytes], ignored_parameters: ParamList = None) -> str:
    """Normalize and filter urlencoded params from either a URL or request body with form data"""
    value = decode(value)
    params = parse_qsl(value)
    params = filter_sort_multidict(params, ignored_parameters)
    query_str = urlencode(params)

    # parse_qsl doesn't handle key-only params, so add those here
    key_only_params = [k for k in value.split('&') if k and '=' not in k]
    if key_only_params:
        key_only_param_str = '&'.join(sorted(key_only_params))
        query_str = f'{query_str}&{key_only_param_str}' if query_str else key_only_param_str

    return query_str


def redact_response(response: CachedResponse, ignored_parameters: ParamList) -> CachedResponse:
    """Redact any ignored parameters (potentially containing sensitive info) from a cached request"""
    if ignored_parameters:
        response.url = filter_url(response.url, ignored_parameters)
        response.request.url = filter_url(response.request.url, ignored_parameters)
        response.headers = CaseInsensitiveDict(
            filter_sort_dict(response.headers, ignored_parameters)
        )
        response.request.headers = CaseInsensitiveDict(
            filter_sort_dict(response.request.headers, ignored_parameters)
        )
        response.request.body = normalize_body(response.request, ignored_parameters)
    return response


def filter_sort_json(data: Union[List, Mapping], ignored_parameters: ParamList):
    if isinstance(data, Mapping):
        return filter_sort_dict(data, ignored_parameters)
    else:
        return filter_sort_list(data, ignored_parameters)


def filter_sort_dict(
    data: Mapping[str, str], ignored_parameters: ParamList = None
) -> Dict[str, str]:
    # Note: Any ignored_parameters present will have their values replaced instead of removing the
    # parameter, so the cache key will still match whether the parameter was present or not.
    ignored_parameters = set(ignored_parameters or [])
    return {k: ('REDACTED' if k in ignored_parameters else v) for k, v in sorted(data.items())}


def filter_sort_multidict(data: KVList, ignored_parameters: ParamList = None) -> KVList:
    ignored_parameters = set(ignored_parameters or [])
    return [(k, 'REDACTED' if k in ignored_parameters else v) for k, v in sorted(data)]


def filter_sort_list(data: List, ignored_parameters: ParamList = None) -> List:
    if not ignored_parameters:
        return sorted(data)
    return [k for k in sorted(data) if k not in set(ignored_parameters)]


def filter_url(url: str, ignored_parameters: ParamList) -> str:
    """Filter ignored parameters out of a URL"""
    # Strip query params from URL, sort and filter, and reassemble into a complete URL
    url_tokens = urlparse(url)
    return urlunparse(
        (
            url_tokens.scheme,
            url_tokens.netloc,
            url_tokens.path,
            url_tokens.params,
            normalize_params(url_tokens.query, ignored_parameters),
            url_tokens.fragment,
        )
    )
