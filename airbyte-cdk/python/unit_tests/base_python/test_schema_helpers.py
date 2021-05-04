import json
import shutil
import sys
import os
from collections import Mapping
from pathlib import Path
from pytest import fixture

from airbyte_cdk.base_python.schema_helpers import JsonSchemaResolver, ResourceSchemaLoader

MODULE = sys.modules[__name__]
MODULE_NAME = MODULE.__name__.split('.')[0]
SCHEMAS_ROOT = "/".join(os.path.abspath(MODULE.__file__).split("/")[:-1]) / Path("schemas")


# TODO refactor ResourceSchemaLoader to completely separate the functionality for reading data from the package
#  and the functionality for resolving schemas
@fixture(autouse=True, scope='session')
def create_and_teardown_schemas_dir():
    os.mkdir(SCHEMAS_ROOT)
    os.mkdir(SCHEMAS_ROOT / "shared")
    yield
    print("WE ARE HERE")
    print(f"DELETING {SCHEMAS_ROOT}")
    shutil.rmtree(SCHEMAS_ROOT)
    print("DONE")


def create_schema(name: str, content: Mapping):
    with open(SCHEMAS_ROOT / f'{name}.json', "w") as f:
        f.write(json.dumps(content))


# Test that a simple schema is loaded correctly
def test_inline_schema_resolves():
    expected_schema = {
        "type": ["null", "object"],
        "properties": {
            "str": {"type": "string"},
            "int": {"type": "integer"},
            "obj": {"type": ["null", "object"], "properties": {"k1": {"type": "string"}}}}
    }

    create_schema("simple_schema", expected_schema)
    resolver = ResourceSchemaLoader(MODULE_NAME)
    actual_schema = resolver.get_schema("simple_schema")
    assert actual_schema == expected_schema


def test_shared_schemas_resolves():
    expected_schema = {
        "type": ["null", "object"],
        "properties": {
            "str": {"type": "string"},
            "int": {"type": "integer"},
            "obj": {"type": ["null", "object"], "properties": {"k1": {"type": "string"}}}}
    }

    partial_schema = {
        "type": ["null", "object"],
        "properties": {
            "str": {"type": "string"},
            "int": {"type": "integer"},
            "obj": {"$ref": "shared_schema.json"}
        }
    }

    referenced_schema = {"type": ["null", "object"], "properties": {"k1": {"type": "string"}}}

    create_schema("complex_schema", partial_schema)
    create_schema("shared/shared_schema", referenced_schema)

    resolver = ResourceSchemaLoader(MODULE_NAME)

    actual_schema = resolver.get_schema("complex_schema")
    assert actual_schema == expected_schema


