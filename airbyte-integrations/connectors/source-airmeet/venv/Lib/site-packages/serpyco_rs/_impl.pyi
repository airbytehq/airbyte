from collections.abc import Sequence
from enum import Enum, IntEnum
from typing import Any, Callable, Generic, TypeVar

from ._meta import ResolverContext

_T = TypeVar('_T')
_I = TypeVar('_I')
_O = TypeVar('_O')

class ValidationError(Exception):
    message: str

class ErrorItem:
    message: str
    instance_path: str

    def __init__(self, message: str, instance_path: str): ...

class SchemaValidationError(ValidationError):
    errors: list[ErrorItem]

class Serializer(Generic[_T]):
    def __init__(self, py_class: BaseType, naive_datetime_to_utc: bool): ...
    def dump(self, value: _T) -> Any: ...
    def load(self, data: Any) -> _T: ...
    def load_query_params(self, data: Any) -> _T: ...

class CustomEncoder(Generic[_I, _O]):
    serialize: Callable[[_I], _O] | None
    deserialize: Callable[[_O], _I] | None

    def __init__(self, serialize: Callable[[_I], _O] | None = None, deserialize: Callable[[_O], _I] | None = None): ...

class BaseType:
    custom_encoder: CustomEncoder[Any, Any] | None

    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None): ...

class ContainerBaseType(BaseType):
    ref_name: str

    def set_usages(self, val: int) -> None: ...
    def should_use_ref(self) -> bool: ...

class NoneType(BaseType):
    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None): ...

class IntegerType(BaseType):
    min: int | None
    max: int | None

    def __init__(
        self, min: int | None = None, max: int | None = None, custom_encoder: CustomEncoder[Any, Any] | None = None
    ): ...

class FloatType(BaseType):
    min: float | None
    max: float | None

    def __init__(self, min: float | None, max: float | None, custom_encoder: CustomEncoder[Any, Any] | None): ...

class DecimalType(BaseType):
    min: float | None
    max: float | None

    def __init__(self, min: float | None, max: float | None, custom_encoder: CustomEncoder[Any, Any] | None): ...

class StringType(BaseType):
    min_length: int | None
    max_length: int | None

    def __init__(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        custom_encoder: CustomEncoder[Any, Any] | None = None,
    ): ...

class BooleanType(BaseType):
    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None): ...

class UUIDType(BaseType):
    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None): ...

class TimeType(BaseType):
    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None): ...

class DateTimeType(BaseType):
    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None): ...

class DateType(BaseType):
    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None): ...

class DefaultValue(Generic[_T]):
    @staticmethod
    def none() -> DefaultValue[None]: ...
    @staticmethod
    def some(value: _T) -> DefaultValue[_T]: ...
    def is_none(self) -> bool: ...

NOT_SET: DefaultValue[None]

class EntityField(BaseType):
    name: str
    dict_key: str
    field_type: BaseType
    required: bool = True
    is_discriminator_field: bool = False
    default: DefaultValue[Any]
    default_factory: DefaultValue[Callable[[], Any]]
    doc: str | None
    is_flattened: bool = False
    is_dict_flatten: bool = False

    def __init__(
        self,
        name: str,
        dict_key: str,
        field_type: BaseType,
        required: bool = True,
        is_discriminator_field: bool = False,
        default: DefaultValue[Any] = ...,
        default_factory: DefaultValue[Callable[[], Any]] | DefaultValue[None] = ...,
        doc: str | None = None,
        is_flattened: bool = False,
        is_dict_flatten: bool = False,
    ): ...

class EntityType(BaseType):
    cls: type[Any]
    name: str
    fields: Sequence[EntityField]
    omit_none: bool
    is_frozen: bool
    used_keys: set[str] | None
    doc: str | None

    def __init__(
        self,
        cls: type[Any],
        name: str,
        fields: Sequence[EntityField],
        omit_none: bool = False,
        is_frozen: bool = False,
        used_keys: set[str] | None = None,
        doc: str | None = None,
        custom_encoder: CustomEncoder[Any, Any] | None = None,
    ): ...

class TypedDictType(BaseType):
    name: str
    fields: Sequence[EntityField]
    omit_none: bool
    doc: str | None
    used_keys: set[str] | None

    def __init__(
        self,
        name: str,
        fields: Sequence[EntityField],
        omit_none: bool = False,
        doc: str | None = None,
        used_keys: set[str] | None = None,
        custom_encoder: CustomEncoder[Any, Any] | None = None,
    ): ...

class ArrayType(ContainerBaseType):
    item_type: BaseType
    min_length: int | None
    max_length: int | None

    def __init__(
        self,
        item_type: BaseType,
        ref_name: str,
        min_length: int | None = None,
        max_length: int | None = None,
        custom_encoder: CustomEncoder[Any, Any] | None = None,
    ): ...

class EnumType(BaseType):
    cls: type[Enum | IntEnum]
    items: list[Any]

    def __init__(
        self, cls: type[Enum | IntEnum], items: list[Any], custom_encoder: CustomEncoder[Any, Any] | None = None
    ): ...

class OptionalType(BaseType):
    inner: BaseType

    def __init__(self, inner: BaseType, custom_encoder: CustomEncoder[Any, Any] | None = None): ...

class DictionaryType(BaseType):
    key_type: BaseType
    value_type: BaseType
    omit_none: bool

    def __init__(
        self,
        key_type: BaseType,
        value_type: BaseType,
        omit_none: bool = False,
        custom_encoder: CustomEncoder[Any, Any] | None = None,
    ): ...

class TupleType(ContainerBaseType):
    item_types: list[BaseType]

    def __init__(
        self,
        item_types: list[BaseType],
        ref_name: str,
        custom_encoder: CustomEncoder[Any, Any] | None = None,
    ): ...

class BytesType(BaseType):
    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None = None): ...

class AnyType(BaseType):
    def __init__(self, custom_encoder: CustomEncoder[Any, Any] | None = None): ...

class UnionType(ContainerBaseType):
    item_types: list[BaseType]

    def __init__(
        self,
        item_types: list[BaseType],
        ref_name: str,
        custom_encoder: CustomEncoder[Any, Any] | None = None,
    ): ...

class DiscriminatedUnionType(ContainerBaseType):
    item_types: dict[str, BaseType]
    dump_discriminator: str
    load_discriminator: str

    def __init__(
        self,
        item_types: dict[str, BaseType],
        dump_discriminator: str,
        load_discriminator: str,
        ref_name: str,
        custom_encoder: CustomEncoder[Any, Any] | None = None,
    ): ...

class LiteralType(BaseType):
    args: list[str | int | Enum]

    def __init__(self, args: list[str | int | Enum], custom_encoder: CustomEncoder[Any, Any] | None = None): ...

class RecursionHolder(BaseType):
    name: str
    state_key: str
    meta: ResolverContext

    def __init__(
        self, name: str, state_key: str, meta: ResolverContext, custom_encoder: CustomEncoder[Any, Any] | None = None
    ): ...
    def get_inner_type(self) -> BaseType: ...

class CustomType(BaseType):
    json_schema: dict[str, Any]

    def __init__(self, custom_encoder: CustomEncoder[Any, Any], json_schema: dict[str, Any]): ...
