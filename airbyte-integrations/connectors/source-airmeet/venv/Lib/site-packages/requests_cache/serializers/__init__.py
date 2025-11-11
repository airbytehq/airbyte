"""Response serialization utilities. See :ref:`serializers` for general usage info.

**Summary:**

The ``cattrs`` library includes a number of `pre-configured converters
<https://cattrs.readthedocs.io/en/latest/preconf.html>`_ that perform some pre-serialization steps
required for specific serialization formats.

The module :py:mod:`requests_cache.serializers.preconf` wraps those converters as serializer
:py:class:`.Stage` objects, which are then combined into a :py:class:`.SerializerPipeline`. Preconf
converters run after the base converter and before the format's ``dumps()`` (or equivalent) method.
For example, for JSON:

* Run base converter (:py:class:`.CattrStage`) to convert :py:class:`.CachedResponse` to a dict
* Run json prconf converter to convert binary response body to base84
* Run ``json.dumps()``

For any optional libraries that aren't installed, the corresponding serializer will be a placeholder
class that raises an ``ImportError`` at initialization time instead of at import time.
"""

# ruff: noqa: F401
from typing import Optional, Union

from .cattrs import CattrStage
from .pipeline import SerializerPipeline, Stage
from .preconf import (
    bson_document_serializer,
    bson_serializer,
    dict_serializer,
    dynamodb_document_serializer,
    json_serializer,
    pickle_serializer,
    safe_pickle_serializer,
    utf8_encoder,
    yaml_serializer,
)

__all__ = [
    'SERIALIZERS',
    'CattrStage',
    'SerializerPipeline',
    'SerializerType',
    'Stage',
    'init_serializer',
    'bson_serializer',
    'bson_document_serializer',
    'dynamodb_document_serializer',
    'dict_serializer',
    'json_serializer',
    'pickle_serializer',
    'safe_pickle_serializer',
    'yaml_serializer',
    'utf8_encoder',
]

SERIALIZERS = {
    'bson': bson_serializer,
    'json': json_serializer,
    'pickle': pickle_serializer,
    'yaml': yaml_serializer,
}

SerializerType = Union[str, SerializerPipeline, Stage]


def init_serializer(
    serializer: Optional[SerializerType], decode_content: bool
) -> Optional[SerializerPipeline]:
    """Intitialze a serializer by name or instance"""
    if not serializer:
        return None

    # Look up a serializer by name, if needed
    if isinstance(serializer, str):
        serializer = SERIALIZERS[serializer]

    # Wrap in a SerializerPipeline, if needed
    if not isinstance(serializer, SerializerPipeline):
        serializer = SerializerPipeline([serializer], name=str(serializer))
    serializer.set_decode_content(decode_content)

    return serializer
