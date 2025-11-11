import abc
from collections.abc import Callable
from typing import Annotated, Any, Generic, Optional, Protocol, TypeVar, Union, cast, overload

from ._custom_types import CustomType
from ._describe import BaseType, describe_type
from ._impl import Serializer as _Serializer
from ._json_schema import get_json_schema
from .metadata import CamelCase, ForceDefaultForOptional, OmitNone


_T = TypeVar('_T', bound=Any)
_D = TypeVar('_D')


class _MultiMapping(Protocol[_T, _D]):
    """Protocol for a multi-mapping type."""

    @abc.abstractmethod
    def __getitem__(self, key: str, /) -> _T: ...

    @overload
    @abc.abstractmethod
    def getall(self, key: str) -> list[_T]: ...
    @overload
    @abc.abstractmethod
    def getall(self, key: str, default: _D) -> Union[list[_T], _D]: ...
    @abc.abstractmethod
    def getall(self, key: str, default: _D = ...) -> Union[list[_T], _D]: ...


class Serializer(Generic[_T]):
    _type_info: BaseType

    def __init__(
        self,
        t: type[_T],
        *,
        camelcase_fields: bool = False,
        omit_none: bool = False,
        force_default_for_optional: bool = False,
        naive_datetime_to_utc: bool = False,
        custom_type_resolver: Optional[Callable[[Any], Optional[CustomType[Any, Any]]]] = None,
    ) -> None:
        """
        Create a serializer for the given type.

        :param t: The type to serialize/deserialize.
        :param camelcase_fields: If True, the serializer will convert field names to camelCase.
        :param omit_none: If True, the serializer will omit None values from the output.
        :param force_default_for_optional: If True, the serializer will force default values for optional fields.
        :param naive_datetime_to_utc: If True, the serializer will convert naive datetimes to UTC.
        :param custom_type_resolver: An optional callable that allows users to add support for their own types.
            This parameter should be a function that takes a type as input and returns an instance of CustomType
            if the user-defined type is supported, or None otherwise.
        """
        if camelcase_fields:
            t = cast(type[_T], Annotated[t, CamelCase])
        if omit_none:
            t = cast(type[_T], Annotated[t, OmitNone])
        if force_default_for_optional:
            t = cast(type[_T], Annotated[t, ForceDefaultForOptional])
        self._type_info = describe_type(t, custom_type_resolver=custom_type_resolver)
        self._schema = get_json_schema(self._type_info)
        self._encoder: _Serializer[_T] = _Serializer(self._type_info, naive_datetime_to_utc)

    def dump(self, value: _T) -> Any:
        """Serialize the given value to a JSON-serializable object.

        :param value: The value to serialize.
        """
        return self._encoder.dump(value)

    def load(self, data: Any) -> _T:
        """Deserialize the given JSON-serializable object to the target type.

        :param data: The data to deserialize.
        """
        return self._encoder.load(data)

    def load_query_params(self, data: _MultiMapping[Any, Any]) -> _T:
        """Deserialize the given query parameters to the target type.

        :param data: The query parameters to deserialize.
        """
        return self._encoder.load_query_params(data)

    def get_json_schema(self) -> dict[str, Any]:
        """Get the JSON schema for the target type."""
        return self._schema
