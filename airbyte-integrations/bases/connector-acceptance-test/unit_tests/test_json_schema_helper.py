#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Any, Iterable, List, Text, Tuple, Union

import pendulum
import pytest
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from connector_acceptance_test.utils.json_schema_helper import JsonSchemaHelper, get_expected_schema_structure, get_object_structure
from pydantic import BaseModel


def records_with_state(records, state, stream_mapping, state_cursor_paths) -> Iterable[Tuple[Any, Any, Any]]:
    """Iterate over records and return cursor value with corresponding cursor value from state"""

    for record in records:
        stream_name = record.record.stream
        stream = stream_mapping[stream_name]
        helper = JsonSchemaHelper(schema=stream.stream.json_schema)
        cursor_field = helper.field(stream.cursor_field)
        record_value = cursor_field.parse(record=record.record.data)
        try:
            if state[stream_name] is None:
                continue

            # first attempt to parse the state value assuming the state object is namespaced on stream names
            state_value = cursor_field.parse(record=state[stream_name], path=state_cursor_paths[stream_name])
        except KeyError:
            try:
                # try second time as an absolute path in state file (i.e. bookmarks -> stream_name -> column -> value)
                state_value = cursor_field.parse(record=state, path=state_cursor_paths[stream_name])
            except KeyError:
                continue
        yield record_value, state_value, stream_name


@pytest.fixture(name="simple_state")
def simple_state_fixture():
    return {
        "my_stream": {
            "id": 11,
            "ts_created": "2014-01-01T22:03:11",
            "ts_updated": "2015-01-01T22:03:11",
        }
    }


@pytest.fixture(name="none_state")
def none_state_fixture():
    return {"my_stream": None}


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
            stream=AirbyteStream(name="my_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh]),
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


def test_absolute_path(records, stream_mapping, singer_state):
    stream_mapping["my_stream"].cursor_field = ["ts_created"]
    paths = {"my_stream": ["bookmarks", "my_stream", "ts_created"]}

    result = records_with_state(records=records, state=singer_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value, stream_name = next(result)

    assert record_value == pendulum.datetime(2015, 11, 1, 22, 3, 11), "record value must be correctly found"
    assert state_value == pendulum.datetime(2014, 1, 1, 22, 3, 11), "state value must be correctly found"


def test_none_state(records, stream_mapping, none_state):
    stream_mapping["my_stream"].cursor_field = ["ts_created"]
    paths = {"my_stream": ["unknown", "ts_created"]}

    result = records_with_state(records=records, state=none_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    assert next(result, None) is None


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
    variant_paths = js_helper.find_nodes(keys=["anyOf", "oneOf"])
    assert len(variant_paths) == 2
    assert variant_paths == [["properties", "f", "anyOf"], ["definitions", "C", "properties", "e", "anyOf"]]
    # TODO: implement validation for pydantic generated objects as well
    # js_helper.validate_variant_paths(variant_paths)


@pytest.mark.parametrize(
    "object, paths",
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
def test_get_object_strucutre(object, paths):
    assert get_object_structure(object) == paths


@pytest.mark.parametrize(
    "schema, paths",
    [
        ({"type": "object", "properties": {"a": {"type": "string"}}}, ["/a"]),
        ({"properties": {"a": {"type": "string"}}}, ["/a"]),
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
def test_get_expected_schema_structure(schema, paths):
    assert paths == get_expected_schema_structure(schema)


@pytest.mark.parametrize(
    "keys, num_paths, last_value",
    [
        (["description"], 1, "Tests that keys can be found inside lists of dicts"),
        (["option1"], 2, {"a_key": "a_value"}),
        (["option2"], 1, ["value1", "value2"]),
        (["nonexistent_key"], 0, None),
        (["option1", "option2"], 3, ["value1", "value2"]),
    ],
)
def test_find_and_get_nodes(keys: List[Text], num_paths: int, last_value: Any):
    schema = {
        "title": "Key_inside_oneOf",
        "description": "Tests that keys can be found inside lists of dicts",
        "type": "object",
        "properties": {
            "credentials": {
                "type": "object",
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "common": {"type": "string", "const": "option1", "default": "option1"},
                            "option1": {"type": "string"},
                        },
                    },
                    {
                        "type": "object",
                        "properties": {
                            "common": {"type": "string", "const": "option2", "default": "option2"},
                            "option1": {"a_key": "a_value"},
                            "option2": ["value1", "value2"],
                        },
                    },
                ],
            }
        },
    }
    schema_helper = JsonSchemaHelper(schema)
    variant_paths = schema_helper.find_nodes(keys=keys)
    assert len(variant_paths) == num_paths

    if variant_paths:
        values_at_nodes = []
        for path in variant_paths:
            values_at_nodes.append(schema_helper.get_node(path))
        assert last_value in values_at_nodes
