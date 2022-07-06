#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from enum import Enum
from typing import Any, Dict, List, TypeVar, Union

try:
    # Supported in future python versions
    from typing import Literal, TypedDict  # type: ignore
except ImportError:
    from typing_extensions import Literal, TypedDict  # type: ignore

JsonEncodable = Union[int, float, str, bool]
JsonDict = Dict[str, Any]


# This issue still seems to be present for python < 3.8: https://github.com/python/mypy/issues/7722
class JsonSchemaMeta(TypedDict, total=False):  # type: ignore
    """JSON schema field definitions. Example usage:

    >>> foo = field(metadata=JsonSchemaMeta(description="A foo that foos"))
    """

    description: str
    title: str
    examples: List
    read_only: bool
    write_only: bool
    # Additional extension properties that will be output prefixed with 'x-' when generating OpenAPI / Swagger schemas
    extensions: Dict[str, Any]


class SchemaType(Enum):
    DRAFT_06 = "Draft6"
    DRAFT_04 = "Draft4"
    SWAGGER_V2 = "2.0"
    SWAGGER_V3 = "3.0"
    # Alias of SWAGGER_V2
    V2 = "2.0"
    # Alias of SWAGGER_V3
    V3 = "3.0"
    OPENAPI_3 = "3.0"


# Retained for backwards compatibility
SwaggerSpecVersion = SchemaType


class _NULL_TYPE:
    """Sentinel value to represent null json values for nullable fields, to distinguish them from `None`
    for omitted fields.
    """

    def __bool__(self) -> Literal[False]:
        return False


NULL = _NULL_TYPE()

T = TypeVar("T")
Nullable = Union[T, _NULL_TYPE]
