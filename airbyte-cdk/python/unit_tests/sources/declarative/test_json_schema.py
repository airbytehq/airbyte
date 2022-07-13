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


@dataclass
class SomeOtherClass(JsonSchemaMixin):
    f: Union[ChildString, ChildInt]
    g: Interface


def test_json_schema():
    json_schema = SomeOtherClass.json_schema()
    pprint.pprint(json_schema)
    assert False
