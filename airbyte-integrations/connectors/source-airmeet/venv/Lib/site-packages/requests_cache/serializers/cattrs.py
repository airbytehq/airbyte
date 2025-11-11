"""
Utilities to break down :py:class:`.CachedResponse` objects into a dict of python builtin types
using `cattrs <https://cattrs.readthedocs.io>`_. This does the majority of the work needed for all
serialization formats.

.. automodsumm:: requests_cache.serializers.cattrs
   :classes-only:
   :nosignatures:

.. automodsumm:: requests_cache.serializers.cattrs
   :functions-only:
   :nosignatures:
"""

from __future__ import annotations

from collections.abc import MutableMapping
from datetime import datetime, timedelta
from decimal import Decimal
from functools import singledispatchmethod
from json import JSONDecodeError
from typing import Callable, Dict, ForwardRef, List, Optional, Union

from cattrs import Converter
from requests.cookies import RequestsCookieJar, cookiejar_from_dict
from requests.exceptions import RequestException
from requests.structures import CaseInsensitiveDict

from .._utils import is_json_content_type
from ..models import CachedResponse, DecodedContent
from .pipeline import Stage

try:
    import ujson as json
except ImportError:
    import json  # type: ignore


class CattrStage(Stage):
    """Base serializer class that does pre/post-processing with  ``cattrs``. This can be used either
    on its own, or as a stage within a :py:class:`.SerializerPipeline`.

    Args:
        factory: A callable that returns a ``cattrs`` converter to start from instead of a new
            ``Converter``. Mainly useful for preconf converters.
        decode_content: Save response body in human-readable format, if possible

    Notes on ``decode_content`` option:

    * Response body will be decoded into a human-readable format (if possible) during serialization,
      and re-encoded during deserialization to recreate the original response body.
    * Supported Content-Types are ``application/*json*`` and ``text/*``. All other types will be saved
      as-is.
    * Decoded responses are saved in a separate ``_decoded_content`` attribute, to ensure that
      ``_content`` is always binary.
    * This is the default behavior for Filesystem, DynamoDB, and MongoDB backends.
    """

    def __init__(
        self,
        factory: Optional[Callable[..., Converter]] = None,
        decode_content: bool = False,
        **kwargs,
    ):
        self.converter = init_converter(factory, **kwargs)
        self.decode_content = decode_content

    @singledispatchmethod
    def dumps(self, value):
        return value

    @dumps.register
    def _(self, value: CachedResponse) -> dict:
        response_dict = self.converter.unstructure(value)
        return _decode_content(value, response_dict) if self.decode_content else response_dict

    @singledispatchmethod
    def loads(self, value):
        return value

    @loads.register
    def _(self, value: MutableMapping) -> CachedResponse:
        return _encode_content(self.converter.structure(value, cl=CachedResponse))


def init_converter(
    factory: Optional[Callable[..., Converter]] = None,
    convert_datetime: bool = True,
    convert_timedelta: bool = True,
) -> Converter:
    """Make a converter to structure and unstructure nested objects within a
    :py:class:`.CachedResponse`

    Args:
        factory: An optional factory function that returns a ``cattrs`` converter
        convert_datetime: May be set to ``False`` for pre-configured converters that already have
            datetime support
    """
    factory = factory or Converter
    try:
        converter = factory(omit_if_default=True)
    # Handle previous versions of cattrs (<22.2) that don't support this argument
    except TypeError:
        converter = factory()

    # Convert datetimes to and from iso-formatted strings
    if convert_datetime:
        converter.register_unstructure_hook(datetime, lambda obj: obj.isoformat() if obj else None)
        converter.register_structure_hook(datetime, _to_datetime)

    # Convert timedeltas to and from float values in seconds
    if convert_timedelta:
        converter.register_unstructure_hook(
            timedelta, lambda obj: obj.total_seconds() if obj else None
        )
        converter.register_structure_hook(timedelta, _to_timedelta)

    # Convert dict-like objects to and from plain dicts
    converter.register_unstructure_hook(RequestsCookieJar, lambda obj: dict(obj.items()))
    converter.register_structure_hook(RequestsCookieJar, lambda obj, cls: cookiejar_from_dict(obj))
    converter.register_unstructure_hook(CaseInsensitiveDict, dict)
    converter.register_structure_hook(
        CaseInsensitiveDict, lambda obj, cls: CaseInsensitiveDict(obj)
    )

    # Tell cattrs to ignore DecodedContent; this will be handled separately in `CattrStage.loads()`
    converter.register_structure_hook(DecodedContent, lambda obj, cls: obj)
    # Same as above, but for cattrs 23.2+. In cattrs terms, this handles the "spillover" after
    # handling DecodedContent with the "union passthrough strategy," which is enabled by default
    # for its pre-configured converters (JsonConverter, etc.).
    converter.register_structure_hook(Union[Dict, List], lambda obj, cls: obj)

    def structure_fwd_ref(obj, cls):
        # python<=3.8: ForwardRef may not have been evaluated yet
        if not cls.__forward_evaluated__:  # pragma: no cover
            cls._evaluate(globals(), locals())
        return converter.structure(obj, cls.__forward_value__)

    # Resolve forward references (required for CachedResponse.history)
    converter.register_unstructure_hook_func(
        lambda cls: cls.__class__ is ForwardRef,
        lambda obj, cls=None: converter.unstructure(obj, cls.__forward_value__ if cls else None),
    )
    converter.register_structure_hook_func(
        lambda cls: cls.__class__ is ForwardRef,
        structure_fwd_ref,
    )

    return converter


def make_decimal_timedelta_converter(**kwargs) -> Converter:
    """Make a converter that uses Decimals instead of floats to represent timedelta objects"""
    converter = Converter(**kwargs)
    converter.register_unstructure_hook(
        timedelta, lambda obj: Decimal(str(obj.total_seconds())) if obj else None
    )
    converter.register_structure_hook(timedelta, _to_timedelta)
    # converter.register_unstructure_hook(float, lambda obj: Decimal(str(obj)) if obj else None)
    # converter.register_structure_hook(float, lambda obj, cls: float(obj) if obj else None)
    return converter


def _decode_content(response: CachedResponse, response_dict: Dict) -> Dict:
    """Decode response body into a human-readable format, if possible"""
    ct_header = response.headers.get('Content-Type', '')

    # Decode body as JSON
    if is_json_content_type(ct_header):
        try:
            response_dict['_decoded_content'] = response.json()
            response_dict.pop('_content', None)
        except (JSONDecodeError, RequestException):
            pass

    # Decode body as text
    if ct_header.startswith('text/'):
        response_dict['_decoded_content'] = response.text
        response_dict.pop('_content', None)

    # Otherwise, it is most likely a binary body
    return response_dict


def _encode_content(response: CachedResponse) -> CachedResponse:
    """Re-encode response body if saved as JSON or text (via ``decode_content=True``).
    This has no effect for a binary response body.
    """
    # The response may have previously been saved with `decode_content=False`
    if response._decoded_content is None:
        return response

    # Encode body as JSON
    if is_json_content_type(response.headers.get('Content-Type')):
        response._decoded_content = json.dumps(response._decoded_content)

    # Encode body back to bytes
    if isinstance(response._decoded_content, str):
        response._content = response._decoded_content.encode('utf-8')
        response._decoded_content = None
        response.encoding = 'utf-8'  # Set encoding explicitly so requests doesn't have to detect it
        response.headers['Content-Length'] = str(len(response._content))  # Size may have changed

    return response


def _convert_floats(value):
    """Workaround for DynamoDB-specific issue with decode_content=True. There doesn't seem to be
    an obvious way to do this with the current converter setup, so need to do it manually here.
    """

    def _float_to_decimal(value: DecodedContent):
        if isinstance(value, list):
            return [_float_to_decimal(v) for v in value]
        elif isinstance(value, dict):
            return {k: _float_to_decimal(v) for k, v in value.items()}
        elif isinstance(value, float):
            return Decimal(str(value))
        else:
            return value

    if isinstance(value, dict) and '_decoded_content' in value:
        value['_decoded_content'] = _float_to_decimal(value['_decoded_content'])
    return value


def _to_datetime(obj, cls) -> datetime:
    if isinstance(obj, str):
        obj = datetime.fromisoformat(obj)
    return obj


def _to_timedelta(obj, cls) -> timedelta:
    if isinstance(obj, (int, float)):
        obj = timedelta(seconds=obj)
    elif isinstance(obj, Decimal):
        obj = timedelta(seconds=float(obj))
    return obj
