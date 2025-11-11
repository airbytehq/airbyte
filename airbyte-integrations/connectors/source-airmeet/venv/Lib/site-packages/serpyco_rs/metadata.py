from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Union

from ._impl import CustomEncoder


@dataclass(frozen=True)
class Min:
    value: Union[int, float]


@dataclass(frozen=True)
class Max:
    value: Union[int, float]


@dataclass(frozen=True)
class MinLength:
    value: int


@dataclass(frozen=True)
class MaxLength:
    value: int


@dataclass(frozen=True)
class Discriminator:
    name: str


@dataclass(frozen=True)
class Alias:
    value: str


class Format(Enum):
    no_format = 'no_format'
    camel_case = 'camel_case'


@dataclass(frozen=True)
class FieldFormat:
    format: Format


CamelCase: FieldFormat = FieldFormat(Format.camel_case)
NoFormat: FieldFormat = FieldFormat(Format.no_format)


@dataclass(frozen=True)
class NoneFormat:
    omit: bool


KeepNone: NoneFormat = NoneFormat(False)
OmitNone: NoneFormat = NoneFormat(True)


@dataclass(frozen=True)
class NoneAsDefaultForOptional:
    use: bool


ForceDefaultForOptional: NoneAsDefaultForOptional = NoneAsDefaultForOptional(True)
KeepDefaultForOptional: NoneAsDefaultForOptional = NoneAsDefaultForOptional(False)


_I = TypeVar('_I')
_O = TypeVar('_O')


def serialize_with(func: Callable[[_I], _O]) -> CustomEncoder[_I, _O]:
    return CustomEncoder[_I, _O](serialize=func)


def deserialize_with(func: Callable[[_O], _I]) -> CustomEncoder[_I, _O]:
    return CustomEncoder[_I, _O](deserialize=func)


@dataclass(frozen=True)
class _Flatten:
    """Flatten the fields of a nested structure into the parent structure.

    Similar to serde's flatten attribute, this allows inlining fields from
    a nested dataclass or collecting additional fields in a dict.

    Examples:
        # Flatten a nested dataclass
        @dataclass
        class Person:
            name: str
            address: Annotated[Address, Flatten]

        # Collect additional fields in a dict
        @dataclass
        class FlexibleData:
            id: str
            extra: Annotated[dict[str, Any], Flatten]
    """


Flatten: _Flatten = _Flatten()
