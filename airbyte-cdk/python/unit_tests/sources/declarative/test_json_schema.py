#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import pprint
from dataclasses import dataclass
from typing import Union

from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin


@dataclass
class Interface(JsonSchemaMixin):
    pass


@dataclass
class ChildString(Interface):
    child_field: str


@dataclass
class ChildInt(Interface):
    int_field: int


InterfaceTypeHint = Union[tuple(Interface.__subclasses__())]


@dataclass
class SomeOtherClass(JsonSchemaMixin):
    f: Union[ChildString, ChildInt]
    g: Interface
    h: InterfaceTypeHint


def test_json_schema():
    json_schema = SomeOtherClass.json_schema()
    pprint.pprint(json_schema)
    # print(json_schema)
    # print()
    # print()
    # json_schema = PydanticSomeOtherClass.schema_json()
    # pprint.pprint(json_schema)
    assert False
