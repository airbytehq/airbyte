#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass, fields
from typing import Union

from airbyte_cdk.sources.declarative.cdk_jsonschema import DEFAULT_SCHEMA_TYPE, JsonDict, JsonSchemaMixin, SchemaType


@dataclass
class Interface(JsonSchemaMixin):
    """This is an interface"""

    # @classmethod
    # @lru_cache
    # def _json_schema(
    #        cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
    # ) -> JsonDict:
    #    print(f"Interface.json_schema with {cls}")
    #    if cls != Interface:
    #        print(f"{cls} is not interface. calling JsonSchemaMixin")
    #        return cls.json_schema()
    #    subclasses = cls.__subclasses__()
    #    if not subclasses:
    #        return cls.get_json_schema()
    #    print(f"subclasses for {cls}: {subclasses}")
    #    t = Union[tuple(subclasses)]


#
#        @dataclass
#        class _anon(JsonSchemaMixin):
#            field: t
#
#        _anon.__name__ = cls.__name__
#        _anon.__doc__ = cls.__doc__
#        return _anon.get_json_schema(embeddable=True)


count = 0


@dataclass
class ChildInterfaceString(Interface, JsonSchemaMixin):
    """ConcreteType1"""

    child_field: str


@dataclass
class ChildInt(Interface):
    """ConcreteType2"""

    int_field: int


#
#    @classmethod
#    def json_schema(
#            cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
#    ) -> JsonDict:
#        return JsonSchemaMixin.json_schema(cls)


InterfaceTypeHint = Union[tuple(Interface.__subclasses__())]


@dataclass
class ConcreteClass(JsonSchemaMixin):
    number: int


@dataclass
class SomeOtherClass(JsonSchemaMixin):
    """Outerobject containing interface"""

    f: int

    g: ConcreteClass
    h: Interface

    @classmethod
    def _json_schema(
        cls, embeddable: bool = False, schema_type: SchemaType = DEFAULT_SCHEMA_TYPE, validate_enums: bool = True, **kwargs
    ) -> JsonDict:
        # Copy class so we don't modify the fields directly
        # copy_cls = type('CopyOfB', cls.__bases__, dict(cls.__dict__))
        copy_mixin = type("Copymixin", cls.__bases__, dict(cls.__dict__))

        class_fields = fields(cls)
        print(cls.__dict__)

        for field in class_fields:
            t = field.type
            if "__subclasses__" in t.__dict__:
                subsclasses = t.__subclasses__()
                if subsclasses and not t.__module__ == "builtins":
                    field.type = Union[tuple(subsclasses)]
                    copy_mixin["__annotations__"][field.name] = Union[tuple(subsclasses)]
        # setattr(copy_mixin, "__dataclass_fields__", cls.__dict__["__dataclass_fields__"])

        copy_mixin.__name__ = cls.__name__
        copy_mixin.__doc__ = cls.__doc__

        # setattr(copy_mixin, "json_schema", InterfaceMixin.json_schema)

        schema = copy_mixin.json_schema(embeddable=True)
        return schema


#    h: InterfaceTypeHint


def test_json_schema():
    # copy the top level class
    copy_cls = type("Copymixin", SomeOtherClass.__bases__, dict(SomeOtherClass.__dict__))

    class_fields = fields(copy_cls)
    # iterate over the fields
    for field in class_fields:
        t = field.type
        subsclasses = t.__subclasses__()
        # Only replace the type if there are subclasses and t is not in builtins
        if subsclasses and t.__module__ != "builtins":
            print(f"subclasses for {field.name}: {subsclasses}")
            # replace the type with union of subclasses
            field.type = Union[tuple(subsclasses)]
            copy_cls.__dict__["__annotations__"][field.name] = Union[tuple(subsclasses)]

    json_schema = copy_cls.json_schema()
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
