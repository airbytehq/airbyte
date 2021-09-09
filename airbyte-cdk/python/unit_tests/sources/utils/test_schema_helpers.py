#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
import os
import shutil
import sys
import traceback
from collections.abc import Mapping
from pathlib import Path

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader, check_config_against_spec_or_exit
from pytest import fixture
from pytest import raises as pytest_raises

logger = AirbyteLogger()


MODULE = sys.modules[__name__]
MODULE_NAME = MODULE.__name__.split(".")[0]
SCHEMAS_ROOT = "/".join(os.path.abspath(MODULE.__file__).split("/")[:-1]) / Path("schemas")


# TODO (sherif) refactor ResourceSchemaLoader to completely separate the functionality for reading data from the package. See https://github.com/airbytehq/airbyte/issues/3222
#  and the functionality for resolving schemas. See https://github.com/airbytehq/airbyte/issues/3222
@fixture(autouse=True, scope="session")
def create_and_teardown_schemas_dir():
    os.mkdir(SCHEMAS_ROOT)
    os.mkdir(SCHEMAS_ROOT / "shared")
    yield
    shutil.rmtree(SCHEMAS_ROOT)


def create_schema(name: str, content: Mapping):
    with open(SCHEMAS_ROOT / f"{name}.json", "w") as f:
        f.write(json.dumps(content))


@fixture
def spec_object():
    spec = {
        "connectionSpecification": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["api_token"],
            "additionalProperties": False,
            "properties": {
                "api_token": {"title": "API Token", "type": "string"},
            },
        },
    }
    yield ConnectorSpecification.parse_obj(spec)


def test_check_config_against_spec_or_exit_does_not_print_schema(capsys, spec_object):
    config = {"super_secret_token": "really_a_secret"}
    with pytest_raises(Exception) as ex_info:
        check_config_against_spec_or_exit(config, spec_object, logger)
        exc = ex_info.value
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        out, err = capsys.readouterr()
        assert "really_a_secret" not in out + err


def test_should_not_fail_validation_for_valid_config(spec_object):
    config = {"api_token": "something"}
    check_config_against_spec_or_exit(config, spec_object, logger)
    assert True, "should pass validation with valid config"


class TestResourceSchemaLoader:
    # Test that a simple schema is loaded correctly
    @staticmethod
    def test_inline_schema_resolves():
        expected_schema = {
            "type": ["null", "object"],
            "properties": {
                "str": {"type": "string"},
                "int": {"type": "integer"},
                "obj": {"type": ["null", "object"], "properties": {"k1": {"type": "string"}}},
            },
        }

        create_schema("simple_schema", expected_schema)
        resolver = ResourceSchemaLoader(MODULE_NAME)
        actual_schema = resolver.get_schema("simple_schema")
        assert actual_schema == expected_schema

    @staticmethod
    def test_shared_schemas_resolves():
        expected_schema = {
            "type": ["null", "object"],
            "properties": {
                "str": {"type": "string"},
                "int": {"type": "integer"},
                "obj": {"type": ["null", "object"], "properties": {"k1": {"type": "string"}}},
            },
        }

        partial_schema = {
            "type": ["null", "object"],
            "properties": {"str": {"type": "string"}, "int": {"type": "integer"}, "obj": {"$ref": "shared_schema.json"}},
        }

        referenced_schema = {"type": ["null", "object"], "properties": {"k1": {"type": "string"}}}

        create_schema("complex_schema", partial_schema)
        create_schema("shared/shared_schema", referenced_schema)

        resolver = ResourceSchemaLoader(MODULE_NAME)

        actual_schema = resolver.get_schema("complex_schema")
        assert actual_schema == expected_schema
