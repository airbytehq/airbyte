import abc
from typing import Any, Generic, TypeVar


_I = TypeVar('_I')
_O = TypeVar('_O')


class CustomType(abc.ABC, Generic[_I, _O]):
    @abc.abstractmethod
    def serialize(self, value: _I) -> _O: ...

    @abc.abstractmethod
    def deserialize(self, value: _O) -> _I: ...

    @abc.abstractmethod
    def get_json_schema(self) -> dict[str, Any]: ...
