#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import functools
import inspect
import json
import re
import sys
import warnings
from dataclasses import MISSING, Field, asdict, dataclass, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union
from uuid import UUID

try:
    from typing import Final, Literal  # type: ignore
except ImportError:
    from typing_extensions import Final, Literal  # type: ignore

from .field_types import (  # noqa: F401
    DateFieldEncoder,
    DateTimeField,
    DateTimeFieldEncoder,
    DecimalField,
    FieldEncoder,
    IPv4AddressField,
    IPv6AddressField,
    UuidField,
)
from .type_defs import _NULL_TYPE, NULL, JsonDict, JsonSchemaMeta, SchemaType  # noqa: F401
from .type_hints import get_class_type_hints

try:
    import fastjsonschema

    def validate_func(data, schema):
        return fastjsonschema.validate(schema, data)

    JsonSchemaValidationError = fastjsonschema.JsonSchemaException
    fast_validation = True
except ImportError:
    import jsonschema

    validate_func = jsonschema.validate
    JsonSchemaValidationError = jsonschema.ValidationError
    fast_validation = False

JSON_ENCODABLE_TYPES = {str: {"type": "string"}, int: {"type": "integer"}, bool: {"type": "boolean"}, float: {"type": "number"}}
SEQUENCE_TYPES = {"Sequence": list, "List": list, "Set": set, "set": set, "list": list}
MAPPING_TYPES = ("Dict", "Mapping", "dict")
TUPLE_TYPES = ("Tuple", "tuple")


class ValidationError(Exception):
    pass


class UnknownEnumValueError(ValueError):
    pass


@functools.lru_cache(maxsize=None)
def get_field_args(field_type: Any) -> tuple:
    field_args = (Any, Any)
    if hasattr(field_type, "__args__") and field_type.__args__ is not None:
        field_args = field_type.__args__
    return field_args


def is_enum(field_type: Any):
    return issubclass_safe(field_type, Enum)


def issubclass_safe(klass: Any, base: Type):
    try:
        return issubclass(klass, base)
    except TypeError:
        return False


def is_optional(field: Any) -> bool:
    try:
        return field.__origin__ == Union and type(None) in field.__args__
    except AttributeError:
        return False


def is_final(field: Any) -> bool:
    try:
        return field.__origin__ == Final
    except AttributeError:
        if sys.version_info[:2] == (3, 6):
            return type(field).__qualname__ == "_Final"
        return False


def is_literal(field: Any) -> bool:
    try:
        return field.__origin__ == Literal
    except AttributeError:
        if sys.version_info[:2] == (3, 6):
            return type(field).__qualname__ == "_Literal"
        return False


def is_nullable(field: Any) -> bool:
    try:
        if sys.version_info[:2] == (3, 6):
            # Hack to get python 3.6 working
            return "_NULL_TYPE" in repr(field)
        return field.__origin__ == Union and _NULL_TYPE in field.__args__
    except AttributeError:
        return False


def unwrap_final(final_type: Any) -> Any:
    return final_type.__args__[0] if sys.version_info[:2] >= (3, 7) else final_type.__type__


def unwrap_optional(optional_type: Any) -> Any:
    idx = optional_type.__args__.index(type(None))
    return Union[optional_type.__args__[:idx] + optional_type.__args__[idx + 1 :]]


def unwrap_nullable(nullable_type: Any) -> Any:
    if sys.version_info[:2] == (3, 6):
        return Union[nullable_type.__args__]
    idx = nullable_type.__args__.index(_NULL_TYPE)
    return Union[nullable_type.__args__[:idx] + nullable_type.__args__[idx + 1 :]]


def schema_reference(schema_type: SchemaType, schema_name: str) -> Dict[str, str]:
    ref_path = "#/components/schemas" if schema_type == SchemaType.SWAGGER_V3 else "#/definitions"
    return {"$ref": "{}/{}".format(ref_path, schema_name)}


_ValueEncoder = Callable[[Any, Any, bool], Any]
_ValueDecoder = Callable[[str, Any, Any], Any]

T = TypeVar("T", bound="JsonSchemaMixin")

# TODO: Remove type ignore once https://github.com/python/mypy/issues/731 is fixed
FieldExcludeList = Tuple[Union[str, Tuple[str, "FieldExcludeList"]], ...]  # type: ignore

DEFAULT_SCHEMA_TYPE = SchemaType.DRAFT_06


@functools.lru_cache()
def _to_camel_case(value: str) -> str:
    if "_" in value:
        parts = value.split("_")
        return "".join([parts[0]] + [part[0].upper() + part[1:] for part in parts[1:]])
    else:
        return value


@dataclass(frozen=True)
class SchemaOptions:
    schema_type: SchemaType
    validate_enums: bool = True


@dataclass
class JsonSchemaField:
    field: Field
    mapped_name: str
    is_property: bool = False


@dataclass
class FieldMeta:
    schema_type: SchemaType
    default: Any = None
    examples: Optional[List] = None
    description: Optional[str] = None
    title: Optional[str] = None
    # OpenAPI 3 only properties
    read_only: Optional[bool] = None
    write_only: Optional[bool] = None
    extensions: Optional[Dict[str, Any]] = None

    @property
    def as_dict(self) -> Dict:
        schema_dict = {_to_camel_case(k): v for k, v in asdict(self).items() if v is not None and k not in ["schema_type", "extensions"]}
        if (self.schema_type in [SchemaType.SWAGGER_V2, SchemaType.OPENAPI_3]) and self.extensions is not None:
            schema_dict.update({"x-" + k: v for k, v in self.extensions.items()})
        # Swagger 2 only supports a single example value per property
        if "examples" in schema_dict and len(schema_dict["examples"]) > 0 and self.schema_type == SchemaType.SWAGGER_V2:
            schema_dict["example"] = schema_dict["examples"][0]
            del schema_dict["examples"]
        return schema_dict


class JsonSchemaMixin:
    """Mixin which adds methods to generate a JSON schema and
    convert to and from JSON encodable dicts with validation against the schema
    """

    _field_encoders: Dict[Type, FieldEncoder] = {
        date: DateFieldEncoder(),
        datetime: DateTimeFieldEncoder(),
        UUID: UuidField(),
        Decimal: DecimalField(),
        IPv4Address: IPv4AddressField(),
        IPv6Address: IPv6AddressField(),
    }

    # Cache of the generated schema
    __schema: Dict[SchemaOptions, JsonDict]
    __compiled_schema: Dict[SchemaOptions, Callable]
    __definitions: Dict[SchemaOptions, JsonDict]
    # Cache of field encode / decode functions
    __encode_cache: Dict[Any, _ValueEncoder]
    __decode_cache: Dict[Any, _ValueDecoder]
    __mapped_fields: List[JsonSchemaField]
    __discriminator_name: Optional[str]
    # True if __discriminator_name is inherited from the base class
    __discriminator_inherited: bool
    __allow_additional_props: bool
    __serialise_properties: Union[Tuple[str, ...], bool]

    @classmethod
    def _discriminator(cls) -> Optional[str]:
        return cls.__discriminator_name

    def __init_subclass__(
        cls,
        discriminator: Optional[Union[str, bool]] = None,
        allow_additional_props: bool = True,
        serialise_properties: Union[Tuple[str, ...], bool] = False,
        **kwargs,
    ):
        # See https://github.com/python/mypy/issues/4660
        super().__init_subclass__(**kwargs)  # type: ignore
        # Initialise caches
        cls.__schema = {}
        cls.__compiled_schema = {}
        cls.__definitions = {}
        cls.__encode_cache = {}
        cls.__decode_cache = {}
        cls.__mapped_fields = []
        cls.__discriminator_inherited = False
        cls.__serialise_properties = serialise_properties
        if discriminator is not None:
            cls.__discriminator_name = discriminator if isinstance(discriminator, str) else f"{cls.__name__}Type"
        else:
            dataclass_bases = [klass for klass in cls.__bases__ if is_dataclass(klass) and issubclass(klass, JsonSchemaMixin)]
            if len(dataclass_bases) > 0:
                if not allow_additional_props:
                    raise TypeError("Dataclass inheritance and additional_props_false=False not currently supported")
                base_discriminators = [base._discriminator() for base in dataclass_bases if base._discriminator() is not None]
                if len(base_discriminators):
                    if len(base_discriminators) > 1:
                        raise TypeError("Multiple bases with discriminators is unsupported")
                    cls.__discriminator_name = base_discriminators[0]
                    cls.__discriminator_inherited = True
            else:
                cls.__discriminator_name = None
        cls.__allow_additional_props = allow_additional_props

    @classmethod
    def field_mapping(cls) -> Dict[str, str]:
        """Defines the mapping of python field names to JSON field names.

        The main use-case is to allow JSON field names which are Python keywords
        """
        return {}

    @classmethod
    def register_field_encoders(cls, field_encoders: Dict[Type, FieldEncoder]):
        """Registers additional custom field encoders. If called on the base, these are added globally.

        The DateTimeFieldEncoder is included by default.
        """
        if cls is not JsonSchemaMixin:
            cls._field_encoders = {**cls._field_encoders, **field_encoders}
        else:
            cls._field_encoders.update(field_encoders)

    @classmethod
    def _encode_field(cls, field_type: Any, value: Any, omit_none: bool) -> Any:  # noqa
        if value is None or value is NULL:
            return value
        try:
            encoder = cls.__encode_cache[field_type]  # type: ignore
        except (KeyError, TypeError):
            # TODO: Use field_type.__origin__ instead of the type name.
            # This has different behaviour between 3.6 & 3.7 however
            field_type_name = cls._get_field_type_name(field_type)
            if field_type in cls._field_encoders:

                def encoder(ft, v, __):
                    return cls._field_encoders[ft].to_wire(v)

            elif is_optional(field_type):

                def encoder(ft, val, o):
                    return cls._encode_field(unwrap_optional(ft), val, o)

            elif is_nullable(field_type):

                def encoder(ft, val, o):
                    return cls._encode_field(unwrap_nullable(ft), val, o)

            elif is_final(field_type):

                def encoder(ft, val, o):
                    return cls._encode_field(unwrap_final(ft), val, o)

            elif is_enum(field_type):

                def encoder(_, v, __):
                    try:
                        return v.value
                    except AttributeError as e:
                        raise UnknownEnumValueError(f"Unknown enum value: {v}") from e

            elif field_type_name == "Union":
                # Attempt to encode the field with each union variant.
                # TODO: Find a more reliable method than this since in the case 'Union[List[str], Dict[str, int]]' this
                # will just output the dict keys as a list
                encoded = None
                for variant in field_type.__args__:
                    try:
                        encoded = cls._encode_field(variant, value, omit_none)
                        break
                    except (TypeError, AttributeError, UnknownEnumValueError):
                        continue
                if encoded is None:
                    raise TypeError("No variant of '{}' matched the type '{}'".format(field_type, type(value)))
                return encoded
            elif field_type_name in MAPPING_TYPES:

                def encoder(ft, val, o):
                    field_args = get_field_args(ft)
                    return {cls._encode_field(field_args[0], k, o): cls._encode_field(field_args[1], v, o) for k, v in val.items()}

            elif field_type_name in SEQUENCE_TYPES or (field_type_name in TUPLE_TYPES and ... in field_type.__args__):

                def encoder(ft, val, o):
                    field_args = get_field_args(ft)
                    return [cls._encode_field(field_args[0], v, o) for v in val]

            elif field_type_name in TUPLE_TYPES:

                def encoder(ft, val, o):
                    return [cls._encode_field(ft.__args__[idx], v, o) for idx, v in enumerate(val)]

            elif cls._is_json_schema_subclass(field_type):
                # Only need to validate at the top level
                def encoder(_, v, o):
                    return v.to_dict(omit_none=o, validate=False)

            elif hasattr(field_type, "__supertype__"):  # NewType field

                def encoder(ft, v, o):
                    return cls._encode_field(ft.__supertype__, v, o)

            else:

                def encoder(_, v, __):
                    return v

            cls.__encode_cache[field_type] = encoder  # type: ignore
        return encoder(field_type, value, omit_none)

    @classmethod
    def _get_fields(cls, base_fields=True) -> List[JsonSchemaField]:
        # print(f"_get_fields for {cls}")

        def _get_fields_uncached():
            dataclass_bases = [klass for klass in cls.__bases__ if is_dataclass(klass) and issubclass(klass, JsonSchemaMixin)]
            base_fields_types = set()
            for base in dataclass_bases:
                base_fields_types |= {(f.name, f.type) for f in fields(base)}

            mapped_fields = []
            type_hints = get_class_type_hints(cls)
            for f in fields(cls):
                # Skip internal fields
                if f.name.startswith("__") or (not base_fields and (f.name, f.type) in base_fields_types):
                    continue
                # Note fields() doesn't resolve forward refs
                f.type = type_hints[f.name]
                mapped_fields.append(JsonSchemaField(f, cls.field_mapping().get(f.name, f.name)))

            if cls.__serialise_properties:
                include_properties = None
                if isinstance(cls.__serialise_properties, tuple):
                    include_properties = set(cls.__serialise_properties)

                members = inspect.getmembers(cls, inspect.isdatadescriptor)
                for name, member in members:
                    if name != "__weakref__" and (include_properties is None or name in include_properties):
                        f = Field(MISSING, None, None, None, None, None, None)
                        f.name = name
                        f.type = member.fget.__annotations__["return"]
                        mapped_fields.append(JsonSchemaField(f, name, is_property=True))

            return mapped_fields

        if not base_fields:
            return _get_fields_uncached()

        if not cls.__mapped_fields:
            cls.__mapped_fields = _get_fields_uncached()
        return cls.__mapped_fields  # type: ignore

    def to_dict(
        self,
        omit_none: bool = True,
        validate: bool = False,
        validate_enums: bool = True,
        schema_type: SchemaType = DEFAULT_SCHEMA_TYPE,
    ) -> JsonDict:
        """Converts the dataclass instance to a JSON encodable dict, with optional JSON schema validation.

        If omit_none (default True) is specified, any items with value None are removed
        """
        data = {}
        for f in self._get_fields():
            value = getattr(self, f.field.name)
            try:
                value = self._encode_field(f.field.type, value, omit_none)
            except UnknownEnumValueError as e:
                warnings.warn(str(e))

            if omit_none and value is None:
                continue
            if value is NULL:
                value = None
            data[f.mapped_name] = value

        if self.__discriminator_name is not None:
            data[self.__discriminator_name] = self.__class__.__name__

        if validate:
            self._validate(data, validate_enums, schema_type)
        return data

    @classmethod
    def _decode_field(cls, field: str, field_type: Any, value: Any) -> Any:  # noqa
        if value is None:
            return NULL if is_nullable(field_type) else None
        decoder = None
        try:
            decoder = cls.__decode_cache[field_type]  # type: ignore
        except (KeyError, TypeError):
            # Replace any nested dictionaries with their targets
            field_type_name = cls._get_field_type_name(field_type)
            # Note: Only literal types composed of primitive values are currently supported
            if type(value) in JSON_ENCODABLE_TYPES and (field_type in JSON_ENCODABLE_TYPES or is_literal(field_type)):
                if is_literal(field_type):

                    def decoder(_, __, val):
                        return val

                else:

                    def decoder(_, ft, val):
                        return ft(val)

            elif cls._is_json_schema_subclass(field_type):

                def decoder(_, ft, val):
                    return ft.from_dict(val, validate=False)

            elif is_nullable(field_type):

                def decoder(f, ft, val):
                    return cls._decode_field(f, unwrap_nullable(ft), val)

            elif is_optional(field_type):

                def decoder(f, ft, val):
                    return cls._decode_field(f, unwrap_optional(ft), val)

            elif is_final(field_type):

                def decoder(f, ft, val):
                    return cls._decode_field(f, unwrap_final(ft), val)

            elif field_type_name == "Union":
                # Attempt to decode the value using each decoder in turn
                decoded = None
                for variant in field_type.__args__:
                    try:
                        decoded = cls._decode_field(field, variant, value)
                        break
                    except (AttributeError, TypeError, ValueError):
                        continue
                if decoded is not None:
                    return decoded
            elif field_type_name in MAPPING_TYPES:

                def decoder(f, ft, val):
                    field_args = get_field_args(ft)
                    return {cls._decode_field(f, field_args[0], k): cls._decode_field(f, field_args[1], v) for k, v in val.items()}

            elif field_type_name in SEQUENCE_TYPES or (field_type_name in TUPLE_TYPES and ... in field_type.__args__):
                seq_type = tuple if field_type_name in TUPLE_TYPES else SEQUENCE_TYPES[field_type_name]

                def decoder(f, ft, val):
                    field_args = get_field_args(ft)
                    return seq_type(cls._decode_field(f, field_args[0], v) for v in val)

            elif field_type_name in TUPLE_TYPES:

                def decoder(f, ft, val):
                    return tuple(cls._decode_field(f, ft.__args__[idx], v) for idx, v in enumerate(val))

            elif field_type in cls._field_encoders:

                def decoder(_, ft, val):
                    return cls._field_encoders[ft].to_python(val)

            elif hasattr(field_type, "__supertype__"):  # NewType field

                def decoder(f, ft, val):
                    return cls._decode_field(f, ft.__supertype__, val)

            elif is_enum(field_type):

                def decoder(_, ft, val):
                    return ft(val)

            elif field_type == Any:

                def decoder(_, __, val):
                    return val

            if decoder is None:
                warnings.warn(f"Unable to decode value for '{field}: {field_type_name}'")
                return value
            cls.__decode_cache[field_type] = decoder
        return decoder(field, field_type, value)

    @classmethod
    def _validate(cls, data: JsonDict, validate_enums: bool = True, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE):
        if schema_type == SchemaType.OPENAPI_3 or schema_type == SchemaType.SWAGGER_V2:
            warnings.warn("Only draft-04, draft-06 and draft-07 schema types are supported for validation")
            schema_type = DEFAULT_SCHEMA_TYPE

        try:
            if fast_validation:
                schema_validator = cls.__compiled_schema.get(SchemaOptions(schema_type, validate_enums))
                if schema_validator is None:
                    formats = {}
                    for encoder in cls._field_encoders.values():
                        schema = encoder.json_schema
                        if "pattern" in schema and "format" in schema:
                            formats[schema["format"]] = schema["pattern"]

                    schema_validator = fastjsonschema.compile(
                        cls.json_schema(schema_type=schema_type, validate_enums=validate_enums), formats=formats
                    )
                    cls.__compiled_schema[SchemaOptions(schema_type, validate_enums)] = schema_validator
                schema_validator(data)
            else:
                validate_func(data, cls.json_schema(schema_type=schema_type, validate_enums=validate_enums))
        except JsonSchemaValidationError as e:
            raise ValidationError(str(e)) from e

    @classmethod
    def from_dict(
        cls: Type[T],
        data: JsonDict,
        validate: bool = True,
        validate_enums: bool = True,
        schema_type: SchemaType = DEFAULT_SCHEMA_TYPE,
    ) -> T:
        """Returns a dataclass instance with all nested classes converted from the dict given"""
        if cls is JsonSchemaMixin:
            raise NotImplementedError

        if cls.__discriminator_name is not None and cls.__discriminator_name in data:
            if data[cls.__discriminator_name] != cls.__name__:
                for subclass in cls.__subclasses__():
                    if subclass.__name__ == data[cls.__discriminator_name]:
                        return subclass.from_dict(data, validate)
                raise TypeError(f"Class '{cls.__name__}' does not match discriminator '{data[cls.__discriminator_name]}'")

        init_values: Dict[str, Any] = {}
        non_init_values: Dict[str, Any] = {}
        if validate:
            cls._validate(data, validate_enums, schema_type)

        for f in cls._get_fields():
            values = init_values if f.field.init else non_init_values
            if f.mapped_name in data or (f.field.default == MISSING and f.field.default_factory == MISSING):  # type: ignore
                try:
                    values[f.field.name] = cls._decode_field(f.field.name, f.field.type, data.get(f.mapped_name))
                except ValueError:
                    ftype = unwrap_optional(f.field.type) if is_optional(f.field.type) else f.field.type
                    if is_enum(ftype):
                        values[f.field.name] = data.get(f.mapped_name)
                    else:
                        raise

        # Need to ignore the type error here, since mypy doesn't know that subclasses are dataclasses
        instance = cls(**init_values)  # type: ignore
        for field_name, value in non_init_values.items():
            setattr(instance, field_name, value)
        return instance

    @classmethod
    def from_object(cls: Type[T], obj: Any, exclude: FieldExcludeList = tuple()) -> T:
        """Returns a dataclass instance from another object (typically an ORM model).
        The `exclude` parameter is a tuple of field names or (field.name, nested_exclude)
        to exclude from the conversion. For example `exclude=('artist_name', ('albums', ('tracks',))` will exclude
        the `artist_name` and `tracks` from related albums
        """
        exclude_dict = dict([(f[0], f[1]) if isinstance(f, tuple) else (f, None) for f in exclude])
        init_values: Dict[str, Any] = {}
        non_init_values: Dict[str, Any] = {}
        for f in cls._get_fields():
            sub_exclude: FieldExcludeList = tuple()
            if f.field.name in exclude_dict:
                if exclude_dict[f.field.name] is None:
                    if f.field.default == MISSING and f.field.default == MISSING:
                        raise ValueError("Excluded fields must have a default value")
                    continue
                else:
                    sub_exclude = exclude_dict[f.field.name]  # type: ignore
            values = init_values if f.field.init else non_init_values
            ft = f.field.type
            if is_optional(ft):
                ft = unwrap_optional(ft)
            field_type_name = cls._get_field_type_name(ft)

            from_value = getattr(obj, f.field.name)
            if from_value is None:
                values[f.field.name] = from_value
            elif cls._is_json_schema_subclass(ft):
                values[f.field.name] = ft.from_object(from_value, exclude=sub_exclude)
            elif is_enum(ft):
                values[f.field.name] = ft(from_value)
            elif field_type_name in ("List", "list") and cls._is_json_schema_subclass(ft.__args__[0]):
                values[f.field.name] = [ft.__args__[0].from_object(v, exclude=sub_exclude) for v in from_value]
            else:
                values[f.field.name] = from_value

        instance = cls(**init_values)  # type: ignore
        for field_name, value in non_init_values.items():
            setattr(instance, field_name, value)
        return instance

    @staticmethod
    def _is_json_schema_subclass(field_type) -> bool:
        return issubclass_safe(field_type, JsonSchemaMixin)

    @classmethod
    def _get_field_meta(cls, field: Field, schema_type: SchemaType) -> Tuple[FieldMeta, bool]:
        required = True
        field_meta = FieldMeta(schema_type=schema_type)
        default_value = MISSING
        if field.default is not MISSING:
            # In case of default value given
            default_value = field.default
        elif field.default_factory is not MISSING and field.default_factory is not None:  # type: ignore
            # In case of a default factory given, we call it
            default_value = field.default_factory()  # type: ignore

        if default_value is not MISSING:
            field_meta.default = cls._encode_field(field.type, default_value, omit_none=False)
            required = False
        if field.metadata is not None:
            if "examples" in field.metadata:
                field_meta.examples = [cls._encode_field(field.type, example, omit_none=False) for example in field.metadata["examples"]]
            if "extensions" in field.metadata:
                field_meta.extensions = field.metadata["extensions"]
            if "description" in field.metadata:
                field_meta.description = field.metadata["description"]
            if "title" in field.metadata:
                field_meta.title = field.metadata["title"]
            if schema_type == SchemaType.OPENAPI_3:
                field_meta.read_only = field.metadata.get("read_only")
                if field_meta.read_only and default_value is MISSING:
                    warnings.warn("Read-only fields should have a default value")
                field_meta.write_only = field.metadata.get("write_only")
        return field_meta, required

    @classmethod
    def _get_field_schema(cls, field: Union[Field, Type], schema_options: SchemaOptions) -> Tuple[JsonDict, bool]:  # noqa
        field_schema: JsonDict = {}
        required = True

        if isinstance(field, Field):
            field_type = field.type
            field_meta, required = cls._get_field_meta(field, schema_options.schema_type)
        else:
            field_type = field
            field_meta = FieldMeta(schema_type=schema_options.schema_type)

        field_type_name = cls._get_field_type_name(field_type)
        field_args = get_field_args(field_type)  # type: ignore
        if cls._is_json_schema_subclass(field_type):
            field_schema = schema_reference(schema_options.schema_type, field_type_name)
        else:
            # If is optional[...]
            if is_optional(field_type):
                field_schema = cls._get_field_schema(unwrap_optional(field_type), schema_options)[0]
                required = False
            elif is_nullable(field_type):
                field_schema, required = cls._get_field_schema(unwrap_nullable(field_type), schema_options)
                if schema_options.schema_type == SchemaType.OPENAPI_3:
                    field_schema["nullable"] = True
                elif schema_options.schema_type != SchemaType.SWAGGER_V2:
                    field_schema = {"oneOf": [field_schema, {"type": "null"}]}
            elif is_final(field_type):
                field_schema, required = cls._get_field_schema(unwrap_final(field_type), schema_options)
            elif is_literal(field_type):
                field_schema = {"enum": list(field_args if sys.version_info[:2] >= (3, 7) else field_type.__values__)}
            elif is_enum(field_type):
                member_types = set()
                values = []
                for member in field_type:
                    member_types.add(type(member.value))
                    values.append(member.value)
                if len(member_types) == 1:
                    member_type = member_types.pop()
                    if member_type in JSON_ENCODABLE_TYPES:
                        field_schema.update(JSON_ENCODABLE_TYPES[member_type])
                    else:
                        field_schema.update(cls._field_encoders[member_types.pop()].json_schema)
                if schema_options.validate_enums:
                    field_schema["enum"] = values

                    # If embedding into a swagger spec add the enum name as an extension.
                    # Note: Unlike swagger, JSON schema does not support extensions
                    if schema_options.schema_type in (SchemaType.SWAGGER_V2, SchemaType.SWAGGER_V3):
                        field_schema["x-enum-name"] = field_type_name
                    if schema_options.schema_type == SchemaType.SWAGGER_V3:
                        field_schema["x-module-name"] = field_type.__module__
            elif field_type_name == "Union":
                if schema_options.schema_type == SchemaType.SWAGGER_V2:
                    raise TypeError("Type unions unsupported in Swagger 2.0")
                field_schema = {"anyOf": [cls._get_field_schema(variant, schema_options)[0] for variant in field_args]}
                field_schema["anyOf"].sort(key=lambda item: item.get("type", ""))
            elif field_type_name in MAPPING_TYPES:
                field_schema = {"type": "object"}
                if field_args[1] is not Any:
                    field_schema["additionalProperties"] = cls._get_field_schema(field_args[1], schema_options)[0]
            elif field_type_name in SEQUENCE_TYPES or (field_type_name in TUPLE_TYPES and ... in field_args):
                # TODO: How do we handle Optional type within lists / tuples
                field_schema = {"type": "array"}
                if field_args[0] is not Any:
                    field_schema["items"] = cls._get_field_schema(field_args[0], schema_options)[0]
                if field_type_name in ("Set", "set"):
                    field_schema["uniqueItems"] = True
            elif field_type_name in TUPLE_TYPES:
                tuple_len = len(field_args)
                # TODO: If there are multiple distinct item_schemas, this is not compliant with OpenAPI 3.0
                item_schemas = [cls._get_field_schema(type_arg, schema_options)[0] for type_arg in field_args]
                field_schema = {
                    "type": "array",
                    "minItems": tuple_len,
                    "maxItems": tuple_len,
                    "items": item_schemas[0] if len(set(field_args)) == 1 else item_schemas,
                }
            elif field_type in JSON_ENCODABLE_TYPES:
                field_schema.update(JSON_ENCODABLE_TYPES[field_type])
            elif field_type in cls._field_encoders:
                field_schema.update(cls._field_encoders[field_type].json_schema)
            elif hasattr(field_type, "__supertype__"):  # NewType fields
                field_schema, _ = cls._get_field_schema(field_type.__supertype__, schema_options)
            else:
                warnings.warn(f"Unable to create schema for '{field_type_name}'")

        field_schema.update(field_meta.as_dict)

        return field_schema, required

    @classmethod
    def _get_field_definitions(cls, field_type: Any, definitions: JsonDict, schema_options: SchemaOptions):
        field_type_name = cls._get_field_type_name(field_type)
        field_args = get_field_args(field_type)

        if is_optional(field_type):
            cls._get_field_definitions(unwrap_optional(field_type), definitions, schema_options)
        elif field_type_name in SEQUENCE_TYPES:
            cls._get_field_definitions(field_args[0], definitions, schema_options)
        elif field_type_name in MAPPING_TYPES:
            cls._get_field_definitions(field_args[1], definitions, schema_options)
        elif field_type_name == "Union":
            for variant in field_type.__args__:
                cls._get_field_definitions(variant, definitions, schema_options)
        elif cls._is_json_schema_subclass(field_type):
            # Prevent recursion from forward refs & circular type dependencies
            if field_type.__name__ not in definitions:
                definitions[field_type.__name__] = None
                definitions.update(
                    field_type.json_schema(
                        embeddable=True, schema_type=schema_options.schema_type, validate_enums=schema_options.validate_enums
                    )
                )

    @classmethod
    def all_json_schemas(cls: Type[T], schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True) -> JsonDict:
        """Returns JSON schemas for all subclasses"""
        definitions = {}
        for subclass in cls.__subclasses__():
            if is_dataclass(subclass):
                definitions.update(subclass.json_schema(embeddable=True, schema_type=schema_type, validate_enums=validate_enums))
            else:
                definitions.update(subclass.all_json_schemas(schema_type=schema_type, validate_enums=validate_enums))
        return definitions

    @classmethod
    def json_schema(
        cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
    ) -> JsonDict:
        """Returns the JSON schema for the dataclass, along with the schema of any nested dataclasses
        within the 'definitions' field.

        Enable the embeddable flag to generate the schema in a format for embedding into other schemas
        or documents supporting JSON schema such as Swagger specs.

        If embedding the schema into a swagger api, specify 'swagger_version' to generate a spec compatible with that
        version.
        """
        if "swagger_version" in kwargs and kwargs["swagger_version"] is not None:
            schema_type = kwargs["swagger_version"]

        schema_options = SchemaOptions(schema_type, validate_enums)
        if schema_options.schema_type in (SchemaType.SWAGGER_V3, SchemaType.SWAGGER_V2) and not embeddable:
            schema_options = SchemaOptions(SchemaType.DRAFT_06, validate_enums)
            warnings.warn("'Swagger schema types unsupported when 'embeddable=False', using 'SchemaType.DRAFT_06'")

        if cls is JsonSchemaMixin:
            warnings.warn(
                "Calling 'JsonSchemaMixin.json_schema' is deprecated. Use 'JsonSchemaMixin.all_json_schemas' instead", DeprecationWarning
            )
            return cls.all_json_schemas(schema_options.schema_type, validate_enums)

        definitions: JsonDict = {}
        if schema_options not in cls.__definitions:
            cls.__definitions[schema_options] = definitions
        else:
            definitions = cls.__definitions[schema_options]

        if schema_options in cls.__schema:
            schema = cls.__schema[schema_options]
        else:
            properties = {}
            required = []
            for f in cls._get_fields(base_fields=False):
                properties[f.mapped_name], is_required = cls._get_field_schema(f.field, schema_options)
                if f.is_property:
                    properties[f.mapped_name]["readOnly"] = True
                cls._get_field_definitions(f.field.type, definitions, schema_options)
                # Only add 'readOnly' properties to required for OpenAPI 3
                if is_required and (not f.is_property or schema_options.schema_type == SchemaType.OPENAPI_3):
                    required.append(f.mapped_name)
            schema = {"type": "object", "required": required, "properties": properties}

            if schema_options.schema_type == SchemaType.OPENAPI_3:
                schema["x-module-name"] = cls.__module__

            if not cls.__allow_additional_props:
                schema["additionalProperties"] = False

            if (
                cls.__discriminator_name is not None
                and schema_options.schema_type == SchemaType.OPENAPI_3
                and not cls.__discriminator_inherited
            ):
                schema["discriminator"] = {"propertyName": cls.__discriminator_name}
                properties[cls.__discriminator_name] = {"type": "string"}
                required.append(cls.__discriminator_name)

            # Needed for Draft 04 backwards compatibility
            if len(required) == 0:
                del schema["required"]

            dataclass_bases = [klass for klass in cls.__bases__ if is_dataclass(klass) and issubclass(klass, JsonSchemaMixin)]
            if len(dataclass_bases) > 0:
                schema = {"allOf": [schema_reference(schema_options.schema_type, base.__name__) for base in dataclass_bases] + [schema]}
                for base in dataclass_bases:
                    definitions.update(
                        base.json_schema(
                            embeddable=True, schema_type=schema_options.schema_type, validate_enums=schema_options.validate_enums
                        )
                    )

            if cls.__doc__:
                schema["description"] = cls.__doc__

            cls.__schema[schema_options] = schema

        if embeddable:
            return {**definitions, cls.__name__: schema}
        else:
            schema_uri = "http://json-schema.org/draft-06/schema#"
            if schema_options.schema_type == SchemaType.DRAFT_04:
                schema_uri = "http://json-shema.org/draft-04/schema#"

            full_schema = {**schema, **{"$schema": schema_uri}}
            if len(definitions) > 0:
                full_schema["definitions"] = definitions
            return full_schema

    @staticmethod
    def _get_field_type_name(field_type: Any) -> str:
        try:
            return field_type.__name__
        except AttributeError:
            # The types in the 'typing' module lack the __name__ attribute
            match = re.match(r"typing\.([A-Za-z]+)", str(field_type))
            return str(field_type) if match is None else match.group(1)

    @classmethod
    def from_json(cls: Type[T], data: Union[str, bytes], validate: bool = True, **json_kwargs) -> T:
        return cls.from_dict(json.loads(data, **json_kwargs), validate)

    def to_json(self, omit_none: bool = True, validate: bool = False, **json_kwargs) -> str:
        return json.dumps(self.to_dict(omit_none, validate), **json_kwargs)
