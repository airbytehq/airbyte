import sys
import typing
from enum import Enum
from functools import singledispatch
from typing import Any, Optional, Union

from .._utils import get_attributes_doc
from ._consts import DEFAULT_REF_PREFIX, SCHEMA_VERSION


if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

from .. import _describe as describe
from ._entities import (
    ArrayType,
    Boolean,
    Config,
    DiscriminatedUnionType,
    Discriminator,
    IntegerType,
    Null,
    NumberType,
    ObjectType,
    RefType,
    Schema,
    StringType,
)


if typing.TYPE_CHECKING:
    from .._main import Serializer


class JsonSchemaBuilder:
    def __init__(self, add_dialect_uri: bool = False, ref_prefix: str = DEFAULT_REF_PREFIX):
        self._definitions: dict[str, Any] = {}
        self._ref_prefix = ref_prefix.rstrip('/')
        self._add_dialect_uri = add_dialect_uri
        self._config = Config(ref_prefix=ref_prefix)

    def build(self, serializer: 'Serializer[Any]') -> dict[str, Any]:
        schema = to_json_schema(serializer._type_info, config=self._config)
        schema_def = schema.dump(self._definitions)
        if self._add_dialect_uri:
            schema_def['$schema'] = SCHEMA_VERSION
        return schema_def

    def get_definitions(self) -> dict[str, Any]:
        return self._definitions


def get_json_schema(t: describe.BaseType) -> dict[str, Any]:
    schema = to_json_schema(t, config=Config())
    definitions: dict[str, Any] = {}
    schema_def = schema.dump(definitions)
    components = {'components': {'schemas': definitions}} if definitions else {}
    return {
        '$schema': SCHEMA_VERSION,
        **schema_def,
        **components,
    }


@singledispatch
def to_json_schema(_: Any, doc: Optional[str] = None, *, config: Config) -> Schema:
    return Schema(description=doc, config=config)


@to_json_schema.register
def _(arg: describe.StringType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return StringType(minLength=arg.min_length, maxLength=arg.max_length, description=doc, config=config)


@to_json_schema.register
def _(arg: describe.NoneType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return Null(config=config)


@to_json_schema.register
def _(arg: describe.IntegerType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return IntegerType(minimum=arg.min, maximum=arg.max, description=doc, config=config)


@to_json_schema.register
def _(_: describe.BytesType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return StringType(format='binary', description=doc, config=config)


@to_json_schema.register
def _(arg: describe.FloatType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return NumberType(minimum=arg.min, maximum=arg.max, description=doc, config=config)


@to_json_schema.register
def _(_: describe.DecimalType, doc: Optional[str] = None, *, config: Config) -> Schema:
    # todo: support min/max
    return Schema(
        oneOf=[
            StringType(format='decimal', config=config),
            NumberType(format='decimal', config=config),
        ],
        description=doc,
        config=config,
    )


@to_json_schema.register
def _(_: describe.BooleanType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return Boolean(config=config, description=doc)


@to_json_schema.register
def _(_: describe.UUIDType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return StringType(format='uuid', description=doc, config=config)


@to_json_schema.register
def _(_: describe.TimeType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return StringType(format='time', description=doc, config=config)


@to_json_schema.register
def _(_: describe.DateTimeType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return StringType(format='date-time', description=doc, config=config)


@to_json_schema.register
def _(_: describe.DateType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return StringType(format='date', description=doc, config=config)


@to_json_schema.register
def _(arg: describe.EnumType, doc: Optional[str] = None, *, config: Config) -> Schema:
    docs = get_attributes_doc(arg.cls)
    enum_values = [item.value for item in arg.items]
    type_ = None
    if (types := {type(item.value) for item in arg.items}) and len(types) == 1:
        type_ = {int: 'integer', str: 'string'}.get(types.pop(), None)

    return Schema(
        type=type_,
        enum=enum_values,
        description=doc,
        config=config,
        additionalArgs={f'x-{item.value}': docs.get(item.name) for item in arg.items},
    )


@to_json_schema.register
def _(arg: describe.OptionalType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return Schema(
        anyOf=[
            Null(config=config),
            to_json_schema(arg.inner, config=config),
        ],
        description=doc,
        config=config,
    )


@to_json_schema.register
def _(arg: describe.EntityType, doc: Optional[str] = None, *, config: Config) -> Schema:
    properties: dict[str, Schema] = {}
    required: list[str] = []
    dict_flatten_value_schema = None

    for prop in arg.fields:
        if prop.is_flattened:
            if isinstance(prop.field_type, describe.EntityType):
                flattened_schema = to_json_schema(prop.field_type, prop.doc, config=config)
                if isinstance(flattened_schema, ObjectType) and flattened_schema.properties:
                    properties.update(flattened_schema.properties)
                    if flattened_schema.required:
                        required.extend(flattened_schema.required)
            elif isinstance(prop.field_type, describe.DictionaryType):
                dict_flatten_value_schema = to_json_schema(prop.field_type.value_type, config=config)
        else:
            properties[prop.dict_key] = to_json_schema(prop.field_type, prop.doc, config=config)
            if prop.required:
                required.append(prop.dict_key)

    return ObjectType(
        properties=properties,
        required=required or None,
        name=arg.name,
        description=arg.doc,
        config=config,
        additionalProperties=dict_flatten_value_schema,
    )


@to_json_schema.register
def _(arg: describe.TypedDictType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return ObjectType(
        properties={prop.dict_key: to_json_schema(prop.field_type, prop.doc, config=config) for prop in arg.fields},
        required=[prop.dict_key for prop in arg.fields if prop.required] or None,
        name=arg.name,
        description=arg.doc,
        config=config,
    )


@to_json_schema.register
def _(arg: describe.ArrayType, doc: Optional[str] = None, *, config: Config) -> Schema:
    schema = ArrayType(
        items=to_json_schema(arg.item_type, config=config),
        minItems=arg.min_length,
        maxItems=arg.max_length,
        description=doc,
        config=config,
    )

    if arg.should_use_ref():
        return RefType(description=doc, name=arg.ref_name, definition=schema, config=config)
    return schema


@to_json_schema.register
def _(arg: describe.DictionaryType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return ObjectType(
        additionalProperties=to_json_schema(arg.value_type, config=config), description=doc, config=config
    )


@to_json_schema.register
def _(arg: describe.TupleType, doc: Optional[str] = None, *, config: Config) -> Schema:
    schema = ArrayType(
        prefixItems=[to_json_schema(item, config=config) for item in arg.item_types],
        minItems=len(arg.item_types),
        maxItems=len(arg.item_types),
        description=doc,
        config=config,
    )
    if arg.should_use_ref():
        return RefType(description=doc, name=arg.ref_name, definition=schema, config=config)
    return schema


@to_json_schema.register
def _(_: describe.AnyType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return Schema(description=doc, config=config)


@to_json_schema.register
def _(holder: describe.RecursionHolder, doc: Optional[str] = None, *, config: Config) -> Schema:
    return RefType(description=doc, name=holder.name, config=config)


@to_json_schema.register
def _(arg: describe.LiteralType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return Schema(
        enum=[arg.value if isinstance(arg, Enum) else arg for arg in arg.args],
        description=doc,
        config=config,
    )


@to_json_schema.register
def _(arg: describe.UnionType, doc: Optional[str] = None, *, config: Config) -> Schema:
    schema = Schema(
        anyOf=[to_json_schema(t, config=config) for t in arg.item_types],
        description=doc,
        config=config,
    )

    if arg.should_use_ref():
        return RefType(description=doc, name=arg.ref_name, definition=schema, config=config)

    return schema


@to_json_schema.register
def _(arg: describe.DiscriminatedUnionType, doc: Optional[str] = None, *, config: Config) -> Schema:
    objects = {
        name: schema
        for name, t in arg.item_types.items()
        if (schema := to_json_schema(t, config=config)) and _check_unions_schema_types(schema)
    }

    schema = DiscriminatedUnionType(
        oneOf=list(objects.values()),
        discriminator=Discriminator(
            property_name=arg.load_discriminator,
            mapping={name: val.ref for name, val in objects.items()},
        ),
        description=doc,
        config=config,
    )
    if arg.should_use_ref():
        return RefType(description=doc, name=arg.ref_name, definition=schema, config=config)

    return schema


def _check_unions_schema_types(schema: Schema) -> TypeGuard[Union[ObjectType, RefType]]:
    if isinstance(schema, (ObjectType, RefType)):
        return True
    raise RuntimeError(f'Unions schema items must be ObjectType or RefType. Current: {schema}')


@to_json_schema.register
def _(arg: describe.CustomType, doc: Optional[str] = None, *, config: Config) -> Schema:
    return Schema(additionalArgs=arg.json_schema, description=doc, config=config)
