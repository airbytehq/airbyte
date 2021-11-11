#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Union

import pendulum
import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from pydantic import BaseModel
from source_acceptance_test.tests.test_incremental import records_with_state
from source_acceptance_test.utils.json_schema_helper import JsonSchemaHelper, get_expected_schema_structure, get_object_structure


@pytest.fixture(name="simple_state")
def simple_state_fixture():
    return {
        "my_stream": {
            "id": 11,
            "ts_created": "2014-01-01T22:03:11",
            "ts_updated": "2015-01-01T22:03:11",
        }
    }


@pytest.fixture(name="nested_state")
def nested_state_fixture(simple_state):
    return {"my_stream": {"some_account_id": simple_state["my_stream"]}}


@pytest.fixture(name="singer_state")
def singer_state_fixture(simple_state):
    return {"bookmarks": simple_state}


@pytest.fixture(name="stream_schema")
def stream_schema_fixture():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "ts_created": {"type": "string", "format": "datetime"},
            "nested": {"type": "object", "properties": {"ts_updated": {"type": "string", "format": "date"}}},
        },
    }


@pytest.fixture(name="stream_mapping")
def stream_mapping_fixture(stream_schema):
    return {
        "my_stream": ConfiguredAirbyteStream(
            stream=AirbyteStream(name="my_stream", json_schema=stream_schema),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.append,
        )
    }


@pytest.fixture(name="records")
def records_fixture():
    return [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="my_stream",
                data={"id": 1, "ts_created": "2015-11-01T22:03:11", "nested": {"ts_updated": "2015-05-01"}},
                emitted_at=0,
            ),
        )
    ]


def test_simple_path(records, stream_mapping, simple_state):
    stream_mapping["my_stream"].cursor_field = ["id"]
    paths = {"my_stream": ["id"]}

    result = records_with_state(records=records, state=simple_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value, stream_name = next(result)

    assert record_value == 1, "record value must be correctly found"
    assert state_value == 11, "state value must be correctly found"


def test_nested_path(records, stream_mapping, nested_state):
    stream_mapping["my_stream"].cursor_field = ["nested", "ts_updated"]
    paths = {"my_stream": ["some_account_id", "ts_updated"]}

    result = records_with_state(records=records, state=nested_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value, stream_name = next(result)

    assert record_value == pendulum.datetime(2015, 5, 1), "record value must be correctly found"
    assert state_value == pendulum.datetime(2015, 1, 1, 22, 3, 11), "state value must be correctly found"


def test_nested_path_unknown(records, stream_mapping, simple_state):
    stream_mapping["my_stream"].cursor_field = ["ts_created"]
    paths = {"my_stream": ["unknown", "ts_created"]}

    result = records_with_state(records=records, state=simple_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    with pytest.raises(KeyError):
        next(result)


def test_absolute_path(records, stream_mapping, singer_state):
    stream_mapping["my_stream"].cursor_field = ["ts_created"]
    paths = {"my_stream": ["bookmarks", "my_stream", "ts_created"]}

    result = records_with_state(records=records, state=singer_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value, stream_name = next(result)

    assert record_value == pendulum.datetime(2015, 11, 1, 22, 3, 11), "record value must be correctly found"
    assert state_value == pendulum.datetime(2014, 1, 1, 22, 3, 11), "state value must be correctly found"


def test_json_schema_helper_mssql(mssql_spec_schema):
    js_helper = JsonSchemaHelper(mssql_spec_schema)
    variant_paths = js_helper.find_variant_paths()
    assert variant_paths == [["properties", "ssl_method", "oneOf"]]
    js_helper.validate_variant_paths(variant_paths)


def test_json_schema_helper_postgres(postgres_source_spec_schema):
    js_helper = JsonSchemaHelper(postgres_source_spec_schema)
    variant_paths = js_helper.find_variant_paths()
    assert variant_paths == [["properties", "replication_method", "oneOf"]]
    js_helper.validate_variant_paths(variant_paths)


def test_json_schema_helper_pydantic_generated():
    class E(str, Enum):
        A = "dda"
        B = "dds"
        C = "ddf"

    class E2(BaseModel):
        e2: str

    class C(BaseModel):
        aaa: int
        e: Union[E, E2]

    class A(BaseModel):
        sdf: str
        sss: str
        c: C

    class B(BaseModel):
        name: str
        surname: str

    class Root(BaseModel):
        f: Union[A, B]

    js_helper = JsonSchemaHelper(Root.schema())
    variant_paths = js_helper.find_variant_paths()
    assert len(variant_paths) == 2
    assert variant_paths == [["properties", "f", "anyOf"], ["definitions", "C", "properties", "e", "anyOf"]]
    # TODO: implement validation for pydantic generated objects as well
    # js_helper.validate_variant_paths(variant_paths)


@pytest.mark.parametrize(
    "object, pathes",
    [
        ({}, []),
        ({"a": 12}, ["/a"]),
        ({"a": {"b": 12}}, ["/a", "/a/b"]),
        ({"a": {"b": 12}, "c": 45}, ["/a", "/a/b", "/c"]),
        (
            {"a": [{"b": 12}]},
            ["/a", "/a/[]", "/a/[]/b"],
        ),
        ({"a": [{"b": 12}, {"b": 15}]}, ["/a", "/a/[]", "/a/[]/b"]),
        ({"a": [[[{"b": 12}, {"b": 15}]]]}, ["/a", "/a/[]", "/a/[]/[]", "/a/[]/[]/[]", "/a/[]/[]/[]/b"]),
    ],
)
def test_get_object_strucutre(object, pathes):
    assert get_object_structure(object) == pathes


@pytest.mark.parametrize(
    "schema, pathes",
    [
        ({"type": "object", "properties": {"a": {"type": "string"}}}, ["/a"]),
        ({"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "number"}}}, ["/a", "/b"]),
        (
            {
                "type": "object",
                "properties": {"a": {"type": "string"}, "b": {"$ref": "#definitions/b_type"}},
                "definitions": {"b_type": {"type": "number"}},
            },
            ["/a", "/b"],
        ),
        ({"type": "object", "oneOf": [{"properties": {"a": {"type": "string"}}}, {"properties": {"b": {"type": "string"}}}]}, ["/a", "/b"]),
        # Some of pydantic generatec schemas have anyOf keyword
        ({"type": "object", "anyOf": [{"properties": {"a": {"type": "string"}}}, {"properties": {"b": {"type": "string"}}}]}, ["/a", "/b"]),
        (
            {"type": "array", "items": {"oneOf": [{"properties": {"a": {"type": "string"}}}, {"properties": {"b": {"type": "string"}}}]}},
            ["/[]/a", "/[]/b"],
        ),
        # There could be an object with any properties with specific type
        ({"type": "object", "properties": {"a": {"type": "object", "additionalProperties": {"type": "string"}}}}, ["/a"]),
        # Array with no item type specified
        ({"type": "array"}, ["/[]"]),
        ({"type": "array", "items": {"type": "object", "additionalProperties": {"type": "string"}}}, ["/[]"]),
    ],
)
def test_get_expected_schema_structure(schema, pathes):
    assert get_expected_schema_structure(schema) == pathes
