#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import pprint
from dataclasses import dataclass, fields
from typing import Union

from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin


@dataclass
class Interface(JsonSchemaMixin):
    """This is an interface"""


count = 0


@dataclass
class ChildInterfaceString(Interface, JsonSchemaMixin):
    """ConcreteType1"""

    child_field: str


@dataclass
class ChildInt(Interface):
    """ConcreteType2"""

    int_field: int


@dataclass
class ConcreteClass(JsonSchemaMixin):
    number: int = 15


@dataclass
class SomeOtherClass(JsonSchemaMixin):
    """Outerobject containing interface"""

    f: int

    g: ConcreteClass
    h: Interface


def test_json_schema():
    # copy the top level class (probably DeclarativeSource?)
    copy_cls = type("Copymixin", SomeOtherClass.__bases__, dict(SomeOtherClass.__dict__))

    class_fields = fields(copy_cls)
    # iterate over the fields
    for field in class_fields:
        t = field.type
        subsclasses = t.__subclasses__()
        # Only replace the type if there are subclasses and t is not in builtins
        if subsclasses and t.__module__ != "builtins":
            # replace the type with union of subclasses
            field.type = Union[tuple(subsclasses)]
            copy_cls.__dict__["__annotations__"][field.name] = Union[tuple(subsclasses)]

    json_schema = copy_cls.json_schema()

    pprint.pprint(json_schema)
    assert "anyOf" in json_schema["properties"]["h"]
