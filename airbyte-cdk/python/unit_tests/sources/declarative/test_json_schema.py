#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass
from functools import lru_cache
from typing import Union

from airbyte_cdk.sources.declarative.cdk_jsonschema import DEFAULT_SCHEMA_TYPE, JsonDict, JsonSchemaMixin, SchemaType


class InterfaceMixin:
    @classmethod
    def full_type_definition(cls):
        return Union[tuple(cls.__subclasses__())]


@dataclass
class Interface(JsonSchemaMixin):
    """This is an interface"""

    @classmethod
    @lru_cache
    def json_schema(
        cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
    ) -> JsonDict:
        print(f"Interface.json_schema with {cls}")
        if cls != Interface:
            print(f"{cls} is not interface. calling JsonSchemaMixin")
            return cls.json_schema()
        subclasses = cls.__subclasses__()
        if not subclasses:
            return cls.get_json_schema()
        print(f"subclasses for {cls}: {subclasses}")
        t = Union[tuple(subclasses)]

        @dataclass
        class _anon(JsonSchemaMixin):
            field: t

        _anon.__name__ = cls.__name__
        _anon.__doc__ = cls.__doc__
        return _anon.get_json_schema(embeddable=True)


count = 0


@dataclass
class ChildInterfaceString(Interface, JsonSchemaMixin):
    """ConcreteType1"""

    child_field: str

    @classmethod
    def json_schema(
        cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
    ) -> JsonDict:
        return cls.get_json_schema(embeddable=True)


@dataclass
class ChildInt(Interface):
    """ConcreteType2"""

    int_field: int

    @classmethod
    def json_schema(
        cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
    ) -> JsonDict:
        return cls.get_json_schema(embeddable=True)


#
#    @classmethod
#    def json_schema(
#            cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
#    ) -> JsonDict:
#        return JsonSchemaMixin.json_schema(cls)


InterfaceTypeHint = Union[tuple(Interface.__subclasses__())]


@dataclass
class SomeOtherClass(JsonSchemaMixin):
    """Outerobject containing interface"""

    #   f: Union[ChildString, ChildInt]
    g: Interface


#    h: InterfaceTypeHint


def test_json_schema():
    json_schema = SomeOtherClass.json_schema()
    # json_schema = get_json_schema(SomeOtherClass)
    import pprint

    print("schema:")
    pprint.pprint(json_schema)
    # definitions = json_schema["definitions"]
    # for c, v in definitions.items():
    #    print(f"c: {c}")
    #    properties = v["properties"]
    #    print(f"v: {v}")
    #    if not properties:
    #        all_json_schemas = Interface.all_json_schemas()
    #        print(f"all_json_schemas for {c}: {all_json_schemas}")
    # print(json_schema)
    # pprint.pprint(Interface.all_json_schemas())

    # print()
    # print()
    # json_schema = PydanticSomeOtherClass.schema_json()
    # pprint.pprint(json_schema)
    assert False
