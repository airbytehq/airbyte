import dataclasses
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum, IntEnum
from functools import cache
from typing import (
    Any,
    ForwardRef,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
    cast,
    get_origin,
    overload,
)
from uuid import UUID

from typing_extensions import (
    TypeGuard,
    assert_never,
    get_args,
    is_typeddict,
)

from ._custom_types import CustomType as CustomTypeMeta
from ._impl import (
    NOT_SET,
    AnyType,
    ArrayType,
    BaseType,
    BooleanType,
    BytesType,
    ContainerBaseType,
    CustomEncoder,
    CustomType,
    DateTimeType,
    DateType,
    DecimalType,
    DefaultValue,
    DictionaryType,
    DiscriminatedUnionType,
    EntityField,
    EntityType,
    EnumType,
    FloatType,
    IntegerType,
    LiteralType,
    NoneType,
    OptionalType,
    RecursionHolder,
    StringType,
    TimeType,
    TupleType,
    TypedDictType,
    UnionType,
    UUIDType,
)
from ._meta import Annotations, ResolverContext
from ._secial_forms import is_union_type, unwrap_special_forms
from ._type_utils import get_type_hints  # type: ignore[attr-defined]
from ._utils import _MergeStack, _Stack, get_attributes_doc, to_camelcase
from .metadata import (
    Alias,
    Discriminator,
    FieldFormat,
    Format,
    KeepNone,
    Max,
    MaxLength,
    Min,
    MinLength,
    NoFormat,
    NoneAsDefaultForOptional,
    NoneFormat,
    OmitNone,
    _Flatten,
)


FrozenInstanceErrors: tuple[type[Exception], ...] = (dataclasses.FrozenInstanceError,)

try:
    import attr
    from attr.exceptions import FrozenInstanceError

    FrozenInstanceErrors += (FrozenInstanceError,)
except ImportError:  # pragma: no cover
    attr = None  # type: ignore


_NoneType = type(None)

_T = TypeVar('_T')


class _TypeResolver:
    resolver_context: _Stack[ResolverContext]
    annotations: _MergeStack[Annotations]
    custom_type_resolver: Optional[Callable[[Any], Optional[CustomTypeMeta[Any, Any]]]]

    def __init__(
        self,
        globals: dict[str, Any],
        custom_type_resolver: Optional[Callable[[Any], Optional[CustomTypeMeta[Any, Any]]]] = None,
    ):
        self.resolver_context = _Stack(ResolverContext(globals=globals))
        self.custom_type_resolver = custom_type_resolver
        self.annotations = _MergeStack(Annotations(NoFormat, KeepNone, KeepNone))

    def resolve(self, t: Any) -> BaseType:
        type_info, _ = self._resolve_with_meta(t)
        return type_info

    def _resolve_with_meta(self, t: Any) -> tuple[BaseType, Annotations]:
        t, metadata = unwrap_special_forms(t)
        with self.annotations.merge(other=metadata):
            context = self.resolver_context.get()
            metadata = self.annotations.get()

            # Try find type in state
            ref = f'{t!r}::{id(t)}::{metadata.key}'
            if context.has_cached_type(ref):
                type_info = context.get_cached_type(ref)

                # for non container types avoid wrap type_info
                if type_info and not isinstance(type_info, ContainerBaseType):
                    return type_info, metadata

                if isinstance(type_info, ContainerBaseType):
                    type_info.set_usages(context.get_usage_count(ref))

                return (
                    RecursionHolder(
                        name=_generate_name(t, ref),
                        state_key=ref,
                        meta=context,
                        custom_encoder=None,
                    ),
                    metadata,
                )

            context.cache_type(ref, None)

            if isinstance(t, ForwardRef):
                t = _evaluate_forwardref(t, self.resolver_context.get())
                return self._resolve_with_meta(t)

            type_info = self._resolve_type(t, ref=ref)
            if isinstance(type_info, ContainerBaseType):
                type_info.set_usages(context.get_usage_count(ref))
            context.cache_type(ref, type_info)

            return type_info, metadata

    def _resolve_type(self, t: Any, ref: str) -> BaseType:
        annotations = self.annotations.get()
        custom_encoder = annotations.get(CustomEncoder)
        name = _generate_name(t, ref)

        if self.custom_type_resolver and (custom_type := self.custom_type_resolver(t)):
            if custom_encoder is None:
                custom_encoder = CustomEncoder(
                    serialize=custom_type.serialize,
                    deserialize=custom_type.deserialize,
                )
            return CustomType(custom_encoder=custom_encoder, json_schema=custom_type.get_json_schema())

        if t is Any:
            return AnyType(custom_encoder=custom_encoder)

        if res := self._match_simple_types(t):
            return res

        origin = get_origin(t) or t
        args = get_args(t)

        # generics types
        if origin in {Sequence, list}:
            min_length_meta = annotations.get(MinLength)
            max_length_meta = annotations.get(MaxLength)

            return ArrayType(
                item_type=(self.resolve(args[0]) if args else AnyType(custom_encoder=None)),
                ref_name=name,
                min_length=min_length_meta.value if min_length_meta else None,
                max_length=max_length_meta.value if max_length_meta else None,
                custom_encoder=custom_encoder,
            )

        if origin in {Mapping, dict}:
            return DictionaryType(
                key_type=(self.resolve(args[0]) if args else AnyType(custom_encoder=None)),
                value_type=(self.resolve(args[1]) if args else AnyType(custom_encoder=None)),
                omit_none=annotations.get(NoneFormat, KeepNone).omit,
                custom_encoder=custom_encoder,
            )

        if origin is tuple:
            if not args or Ellipsis in args:
                raise RuntimeError('Variable length tuples are not supported')
            return TupleType(
                item_types=[self.resolve(arg) for arg in args],
                ref_name=name,
                custom_encoder=custom_encoder,
            )

        if dataclasses.is_dataclass(origin) or _is_attrs(origin) or is_typeddict(origin):
            entity_type = self._describe_entity(
                t=t,
                name=_generate_name(t, ref),
                custom_encoder=custom_encoder,
            )
            return entity_type

        if _is_literal_type(origin):
            if args and _is_supported_literal_args(args):
                return LiteralType(args=list(args), custom_encoder=custom_encoder)
            raise RuntimeError('Supported only Literal[str | int, ...]')

        if is_union_type(origin):
            if _NoneType in args and len(args) == 2:
                new_arg = next(arg for arg in args if arg is not _NoneType)
                return OptionalType(
                    inner=self.resolve(new_arg),
                    custom_encoder=None,
                )

            discriminator = annotations.get(Discriminator)
            if not discriminator:
                return UnionType(
                    item_types=[self.resolve(arg) for arg in args],
                    ref_name=name,
                    custom_encoder=custom_encoder,
                )

            if not all(
                _applies_to_type_or_origin(arg, dataclasses.is_dataclass) or _applies_to_type_or_origin(arg, _is_attrs)
                for arg in args
            ):
                raise RuntimeError(f'Unions supported only for dataclasses or attrs. Provided: {t}')

            with self.resolver_context.push(
                dataclasses.replace(self.resolver_context.get(), discriminator_field=discriminator.name)
            ):
                return DiscriminatedUnionType(
                    item_types={
                        _get_discriminator_value(get_origin(arg) or arg, discriminator.name): self.resolve(arg)
                        for arg in args
                    },
                    ref_name=name,
                    dump_discriminator=discriminator.name,
                    load_discriminator=_apply_format(annotations.get(FieldFormat, NoFormat), discriminator.name),
                    custom_encoder=custom_encoder,
                )

        if isinstance(t, TypeVar):
            raise RuntimeError(f'Unfilled TypeVar: {t}')

        raise RuntimeError(f'Unknown type {t!r}')

    def _match_simple_types(self, t: Any) -> Optional[BaseType]:
        if not isinstance(t, type):
            return None

        annotations = self.annotations.get()
        custom_encoder = annotations.get(CustomEncoder)

        simple_type_mapping: Mapping[type, type[BaseType]] = {
            bytes: BytesType,
            bool: BooleanType,
            date: DateType,
            time: TimeType,
            datetime: DateTimeType,
            UUID: UUIDType,
            _NoneType: NoneType,
        }

        if simple := simple_type_mapping.get(t):
            return simple(custom_encoder=custom_encoder)

        number_type_mapping: Mapping[type, type[Union[IntegerType, FloatType]]] = {
            int: IntegerType,
            float: FloatType,
        }

        if number_type := number_type_mapping.get(t):
            min_meta = annotations.get(Min)
            max_meta = annotations.get(Max)
            return number_type(
                min=cast(Any, min_meta.value) if min_meta else None,
                max=cast(Any, max_meta.value) if max_meta else None,
                custom_encoder=custom_encoder,
            )

        if t is Decimal:
            min_meta = annotations.get(Min)
            max_meta = annotations.get(Max)
            return DecimalType(
                min=min_meta.value if min_meta else None,
                max=max_meta.value if max_meta else None,
                custom_encoder=custom_encoder,
            )

        if t is str:
            min_length_meta = annotations.get(MinLength)
            max_length_meta = annotations.get(MaxLength)

            return StringType(
                min_length=min_length_meta.value if min_length_meta else None,
                max_length=max_length_meta.value if max_length_meta else None,
                custom_encoder=custom_encoder,
            )

        if issubclass(t, (Enum, IntEnum)):
            return EnumType(cls=t, items=list(t), custom_encoder=custom_encoder)

        return None

    def _validate_flatten_fields(self, fields: list[EntityField], t: Any) -> None:
        dict_flatten_fields = []
        struct_flatten_fields = []
        regular_field_keys = set()

        for field in fields:
            if field.is_flattened:
                if isinstance(field.field_type, DictionaryType):
                    dict_flatten_fields.append(field)
                elif isinstance(field.field_type, (EntityType, TypedDictType)):
                    struct_flatten_fields.append(field)
                else:
                    raise RuntimeError(
                        f"Flatten field '{field.name}' has type '{type(field.field_type).__name__}' "
                        f'which cannot be flattened. Only dataclasses, TypedDict, and dict types '
                        f'can be used with Flatten annotation.'
                    )
            else:
                regular_field_keys.add(field.dict_key)

        if len(dict_flatten_fields) > 1:
            field_names = [field.name for field in dict_flatten_fields]
            raise RuntimeError(
                f'Multiple dict flatten fields are not allowed in {t!r}. '
                f'Found flatten dict fields: {field_names}. '
                f'Use only one Annotated[dict[str, Any], Flatten] field per dataclass.'
            )

        for struct_field in struct_flatten_fields:
            struct_type = cast(Union[EntityType, TypedDictType], struct_field.field_type)
            for nested_field in struct_type.fields:
                if nested_field.dict_key in regular_field_keys:
                    raise RuntimeError(
                        f"Field name conflict in {t!r}: '{nested_field.dict_key}' from "
                        f"flattened struct field '{struct_field.name}' conflicts with regular field. "
                        f'Use Alias annotation to rename one of the conflicting fields.'
                    )

    def _compute_used_keys(self, fields: list[EntityField]) -> set[str]:
        has_dict_flatten = any(field.is_dict_flatten for field in fields)
        if not has_dict_flatten:
            return set()

        used_keys: set[str] = set()

        for field in fields:
            if field.is_flattened and isinstance(field.field_type, (EntityType, TypedDictType)):
                struct_type = field.field_type
                for nested_field in struct_type.fields:
                    used_keys.add(nested_field.dict_key)
            else:
                used_keys.add(field.dict_key)

        return used_keys

    def _describe_entity(
        self,
        t: Any,
        name: str,
        custom_encoder: Optional[CustomEncoder[Any, Any]],
    ) -> Union[EntityType, TypedDictType]:
        # PEP-484: Replace all unfilled type parameters with Any
        if get_origin(t) is None and getattr(t, '__parameters__', None):
            t = t[(Any,) * len(t.__parameters__)]

        origin = get_origin(t) or t
        docs = get_attributes_doc(t)
        try:
            types = get_type_hints(t, include_extras=True)
        except Exception:  # pylint: disable=broad-except
            types = {}

        discriminator_field = self.resolver_context.get().discriminator_field

        cls_annotations = self.annotations.get()

        with self.resolver_context.push(
            dataclasses.replace(self.resolver_context.get(), globals=_get_globals(t), discriminator_field=None)
        ):
            fields = []
            for field in _get_entity_fields(origin):
                type_ = types.get(field.name, field.type)

                if isinstance(type_, str):
                    type_ = ForwardRef(
                        type_,
                        module=t.__module__,
                        is_class=True,
                    )
                field_type, field_metadata = self._resolve_with_meta(type_)
                with self.annotations.merge(field_metadata) as field_annotations:
                    alias = field_annotations.get(Alias)
                    none_as_default_for_optional = field_annotations.get(NoneAsDefaultForOptional)
                    flatten = field_annotations.get(_Flatten)

                    is_discriminator_field = field.name == discriminator_field
                    required = (
                        not (field.default != NOT_SET or field.default_factory != NOT_SET) or is_discriminator_field
                    )

                    default = field.default
                    if (
                        isinstance(field_type, OptionalType)
                        and required
                        and none_as_default_for_optional
                        and none_as_default_for_optional.use
                    ):
                        default = DefaultValue.some(None)
                        required = False

                    is_flattened = flatten is not None
                    is_dict_flatten = is_flattened and isinstance(field_type, DictionaryType)

                    fields.append(
                        EntityField(
                            name=field.name,
                            dict_key=(
                                alias.value if alias else _apply_format(cls_annotations.get(FieldFormat), field.name)
                            ),
                            doc=docs.get(field.name),
                            field_type=field_type,
                            default=default,
                            default_factory=field.default_factory,
                            is_discriminator_field=is_discriminator_field,
                            required=required,
                            is_flattened=is_flattened,
                            is_dict_flatten=is_dict_flatten,
                        )
                    )

            self._validate_flatten_fields(fields, t)
            used_keys = self._compute_used_keys(fields)

            if is_typeddict(origin):
                return TypedDictType(
                    name=name,
                    fields=fields,
                    omit_none=cls_annotations.get(NoneFormat) is OmitNone,
                    doc=t.__doc__,
                    custom_encoder=custom_encoder,
                    used_keys=used_keys,
                )

            return EntityType(
                cls=origin,
                name=name,
                fields=fields,
                omit_none=cls_annotations.get(NoneFormat) is OmitNone,
                is_frozen=_is_frozen_dataclass(origin, fields[0]) if fields else False,
                doc=_get_dataclass_doc(t),
                custom_encoder=custom_encoder,
                used_keys=used_keys,
            )


def describe_type(
    t: Any,
    meta: Optional[ResolverContext] = None,
    custom_type_resolver: Optional[Callable[[Any], Optional[CustomTypeMeta[Any, Any]]]] = None,
) -> BaseType:
    return _TypeResolver(_get_globals(t), custom_type_resolver).resolve(t)


@dataclasses.dataclass
class _Field(Generic[_T]):
    name: str
    type: Union[type[_T], str, Any]
    default: Union[DefaultValue[_T], DefaultValue[None]] = NOT_SET
    default_factory: Union[DefaultValue[Callable[[], _T]], DefaultValue[None]] = NOT_SET


def _get_entity_fields(t: Any) -> Sequence[_Field[Any]]:
    if dataclasses.is_dataclass(t):
        return [
            _Field(
                name=f.name,
                type=f.type,
                default=(DefaultValue.some(f.default) if f.default is not dataclasses.MISSING else NOT_SET),
                default_factory=(
                    DefaultValue.some(f.default_factory) if f.default_factory is not dataclasses.MISSING else NOT_SET
                ),
            )
            for f in dataclasses.fields(t)
        ]
    if is_typeddict(t):
        return [
            _Field(
                name=field_name,
                type=field_type,
                default=NOT_SET if _is_required_in_typeddict(t, field_name) else DefaultValue.some(None),
                default_factory=NOT_SET,
            )
            for field_name, field_type in t.__annotations__.items()
        ]
    if _is_attrs(t):
        assert attr
        return [
            _Field(
                name=f.name,
                type=f.type,
                default=(
                    DefaultValue.some(f.default)
                    if (
                        f.default is not attr.NOTHING and not isinstance(f.default, attr.Factory)  # type: ignore[arg-type]
                    )
                    else NOT_SET
                ),
                default_factory=(
                    DefaultValue.some(f.default.factory)  # pyright: ignore
                    if isinstance(f.default, attr.Factory)  # type: ignore[arg-type]
                    else NOT_SET
                ),
            )
            for f in attr.fields(t)
        ]

    raise RuntimeError(f"Unsupported type '{t}'")


@overload
def _find_metadata(annotations: Iterable[Any], type_: type[_T], default: _T) -> _T: ...


@overload
def _find_metadata(annotations: Iterable[Any], type_: type[_T], default: None = None) -> Optional[_T]: ...


def _find_metadata(annotations: Iterable[Any], type_: type[_T], default: Optional[_T] = None) -> Optional[_T]:
    return next((ann for ann in annotations if isinstance(ann, type_)), default)


def _apply_format(f: Optional[FieldFormat], value: str) -> str:
    if not f or f.format is Format.no_format:
        return value
    if f.format is Format.camel_case:
        return to_camelcase(value)
    assert_never(f.format)


_NAME_CACHE = {}


@cache
def _generate_name(cls: Any, ref: str) -> str:
    """
    Generate unique name for entity type.

    We need unique name to avoid name conflicts in generated json schema,
    when we have one entity with different Annotated metadata (like FieldFormat).
    """
    name = repr(cls).removeprefix("<class '").removesuffix("'>")
    if name not in _NAME_CACHE:
        _NAME_CACHE[name] = 0
        return name

    _NAME_CACHE[name] += 1
    return f'{name}{_NAME_CACHE[name]}'


def _get_globals(t: Any) -> dict[str, Any]:
    if t.__module__ in sys.modules:
        return sys.modules[t.__module__].__dict__.copy()
    return {}


def _evaluate_forwardref(t: ForwardRef, meta: ResolverContext) -> Any:
    return t._evaluate(meta.globals, {}, recursive_guard=frozenset[str]())


def _get_discriminator_value(t: Any, name: str) -> str:
    fields = attr.fields(t) if attr and _is_attrs(t) else dataclasses.fields(t)
    for field in fields:
        if field.name == name:
            if _is_literal_type(field.type):
                args = get_args(field.type)
                if len(args) != 1:
                    raise RuntimeError(
                        f'Type {t} has invalid discriminator field "{name}". '
                        f'Discriminator supports only Literal[...] with one argument.'
                    )
                arg = args[0]

                if isinstance(arg, Enum):
                    arg = arg.value

                if isinstance(arg, str):
                    return arg

            raise RuntimeError(
                f'Type {t} has invalid discriminator field "{name}" with type "{field.type!r}". '
                f'Discriminator supports Literal[<str>], Literal[Enum] with str values.'
            )
    raise RuntimeError(f'Type {t} does not have discriminator field "{name}"')


def _is_str_literal(t: Any) -> bool:
    if _is_literal_type(t):
        args = get_args(t)
        if args and all(isinstance(arg, str) for arg in args):
            return True
    return False


def _is_literal_type(t: Any) -> bool:
    return t is Literal or get_origin(t) is Literal


def _is_attrs(t: Any) -> bool:
    return attr is not None and attr.has(t)


def _is_required_in_typeddict(t: Any, key: str) -> bool:
    if is_typeddict(t):
        if t.__total__:
            return key not in t.__optional_keys__
        return key in t.__required_keys__
    raise RuntimeError(f'Expected TypedDict, got "{t!r}"')


def _get_dataclass_doc(cls: Any) -> Optional[str]:
    """Dataclass has automatically generated docstring, which is not very useful."""
    doc: str = cls.__doc__
    if doc is None or doc.startswith(f'{cls.__name__}('):
        return None
    return doc


def _is_frozen_dataclass(cls: Any, field: EntityField) -> bool:
    try:
        obj = object.__new__(cls)
        setattr(obj, field.name, None)
    except FrozenInstanceErrors:
        return True
    else:
        return False


def _is_supported_literal_args(args: Sequence[Any]) -> TypeGuard[list[Union[str, int, Enum]]]:
    return all(isinstance(arg, (str, int, Enum)) for arg in args)


def _applies_to_type_or_origin(t: Any, predicate: Callable[[Any], bool]) -> bool:
    if predicate(t):
        return True
    if hasattr(t, '__origin__'):
        return predicate(t.__origin__)
    return False
