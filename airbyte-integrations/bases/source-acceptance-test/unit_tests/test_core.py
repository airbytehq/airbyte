#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.models import (
    AirbyteErrorTraceMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Level,
    TraceType,
    Type,
)
from source_acceptance_test.config import BasicReadTestConfig
from source_acceptance_test.tests.test_core import TestBasicRead as _TestBasicRead
from source_acceptance_test.tests.test_core import TestDiscovery as _TestDiscovery

from .conftest import does_not_raise


@pytest.mark.parametrize(
    "schema, cursors, should_fail",
    [
        ({}, ["created"], True),
        ({"properties": {"created": {"type": "string"}}}, ["created"], False),
        ({"properties": {"created_at": {"type": "string"}}}, ["created"], True),
        ({"properties": {"created": {"type": "string"}}}, ["updated", "created"], True),
        ({"properties": {"updated": {"type": "object", "properties": {"created": {"type": "string"}}}}}, ["updated", "created"], False),
        ({"properties": {"created": {"type": "object", "properties": {"updated": {"type": "string"}}}}}, ["updated", "created"], True),
    ],
)
def test_discovery(schema, cursors, should_fail):
    t = _TestDiscovery()
    discovered_catalog = {
        "test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema, "default_cursor_field": cursors})
    }
    if should_fail:
        with pytest.raises(AssertionError):
            t.test_defined_cursors_exist_in_schema(discovered_catalog)
    else:
        t.test_defined_cursors_exist_in_schema(discovered_catalog)


@pytest.mark.parametrize(
    "schema, should_fail",
    [
        ({}, False),
        ({"$ref": None}, True),
        ({"properties": {"user": {"$ref": None}}}, True),
        ({"properties": {"user": {"$ref": "user.json"}}}, True),
        ({"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}}, False),
        ({"properties": {"fake_items": {"type": "array", "items": {"$ref": "fake_item.json"}}}}, True),
        (
            {
                "properties": {
                    "fake_items": {
                        "oneOf": [{"type": "object", "$ref": "fake_items_1.json"}, {"type": "object", "$ref": "fake_items_2.json"}]
                    }
                }
            },
            True,
        ),
    ],
)
def test_ref_in_discovery_schemas(schema, should_fail):
    t = _TestDiscovery()
    discovered_catalog = {"test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema})}
    if should_fail:
        with pytest.raises(AssertionError):
            t.test_defined_refs_exist_in_schema(discovered_catalog)
    else:
        t.test_defined_refs_exist_in_schema(discovered_catalog)


@pytest.mark.parametrize(
    "schema, keyword, should_fail",
    [
        ({}, "allOf", False),
        ({"allOf": [{"type": "string"}, {"maxLength": 1}]}, "allOf", True),
        ({"type": "object", "properties": {"allOf": {"type": "string"}}}, "allOf", False),
        ({"type": "object", "properties": {"name": {"allOf": [{"type": "string"}, {"maxLength": 1}]}}}, "allOf", True),
        (
            {"type": "object", "properties": {"name": {"type": "array", "items": {"allOf": [{"type": "string"}, {"maxLength": 4}]}}}},
            "allOf",
            True,
        ),
        (
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "array",
                        "items": {"anyOf": [{"type": "number"}, {"allOf": [{"type": "string"}, {"maxLength": 4}, {"minLength": 2}]}]},
                    }
                },
            },
            "allOf",
            True,
        ),
        ({"not": {"type": "string"}}, "not", True),
        ({"type": "object", "properties": {"not": {"type": "string"}}}, "not", False),
        ({"type": "object", "properties": {"name": {"not": {"type": "string"}}}}, "not", True),
    ],
)
def test_keyword_in_discovery_schemas(schema, keyword, should_fail):
    t = _TestDiscovery()
    discovered_catalog = {"test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema})}
    if should_fail:
        with pytest.raises(AssertionError):
            t.test_defined_keyword_exist_in_schema(keyword, discovered_catalog)
    else:
        t.test_defined_keyword_exist_in_schema(keyword, discovered_catalog)


@pytest.mark.parametrize(
    "discovered_catalog, expectation",
    [
        ({"test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": {}})}, pytest.raises(AssertionError)),
        (
            {"test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": {}, "supported_sync_modes": []})},
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream": AirbyteStream.parse_obj(
                    {"name": "test_stream", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]}
                )
            },
            does_not_raise(),
        ),
        (
            {"test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": {}, "supported_sync_modes": ["full_refresh"]})},
            does_not_raise(),
        ),
        (
            {"test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": {}, "supported_sync_modes": ["incremental"]})},
            does_not_raise(),
        ),
    ],
)
def test_supported_sync_modes_in_stream(discovered_catalog, expectation):
    t = _TestDiscovery()
    with expectation:
        t.test_streams_has_sync_modes(discovered_catalog)


@pytest.mark.parametrize(
    "discovered_catalog, expectation",
    [
        ({"test_stream_1": AirbyteStream.parse_obj({"name": "test_stream_1", "json_schema": {}})}, does_not_raise()),
        (
            {"test_stream_2": AirbyteStream.parse_obj({"name": "test_stream_2", "json_schema": {"additionalProperties": True}})},
            does_not_raise(),
        ),
        (
            {"test_stream_3": AirbyteStream.parse_obj({"name": "test_stream_3", "json_schema": {"additionalProperties": False}})},
            pytest.raises(AssertionError),
        ),
        (
            {"test_stream_4": AirbyteStream.parse_obj({"name": "test_stream_4", "json_schema": {"additionalProperties": "foo"}})},
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_5": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_5",
                        "json_schema": {"additionalProperties": True, "properties": {"my_object": {"additionalProperties": True}}},
                    }
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_6": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_6",
                        "json_schema": {"additionalProperties": True, "properties": {"my_object": {"additionalProperties": False}}},
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
    ],
)
def test_additional_properties_is_true(discovered_catalog, expectation):
    t = _TestDiscovery()
    with expectation:
        t.test_additional_properties_is_true(discovered_catalog)


@pytest.mark.parametrize(
    "schema, record, should_fail",
    [
        ({"type": "object"}, {"aa": 23}, False),
        ({"type": "object"}, {}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"aa": 23}, True),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"created": "23"}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"root": {"created": "23"}}, True),
        # Recharge shop stream case
        (
            {"type": "object", "properties": {"shop": {"type": ["null", "object"]}, "store": {"type": ["null", "object"]}}},
            {"shop": {"a": "23"}, "store": {"b": "23"}},
            False,
        ),
    ],
)
def test_read(schema, record, should_fail):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
    input_config = BasicReadTestConfig()
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=111))
    ]
    t = _TestBasicRead()
    if should_fail:
        with pytest.raises(AssertionError, match="stream should have some fields mentioned by json schema"):
            t.test_read(None, catalog, input_config, [], docker_runner_mock, MagicMock())
    else:
        t.test_read(None, catalog, input_config, [], docker_runner_mock, MagicMock())


@pytest.mark.parametrize(
    "output, expect_trace_message_on_failure, should_fail",
    [
        (
            [
                AirbyteMessage(
                    type=Type.TRACE,
                    trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=111, error=AirbyteErrorTraceMessage(message="oh no")),
                )
            ],
            True,
            False,
        ),
        (
            [
                AirbyteMessage(
                    type=Type.LOG,
                    log=AirbyteLogMessage(level=Level.ERROR, message="oh no"),
                ),
                AirbyteMessage(
                    type=Type.TRACE,
                    trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=111, error=AirbyteErrorTraceMessage(message="oh no")),
                ),
            ],
            True,
            False,
        ),
        (
            [
                AirbyteMessage(
                    type=Type.TRACE,
                    trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=111, error=AirbyteErrorTraceMessage(message="oh no")),
                ),
                AirbyteMessage(
                    type=Type.TRACE,
                    trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=112, error=AirbyteErrorTraceMessage(message="oh no!!")),
                ),
            ],
            True,
            False,
        ),
        (
            [
                AirbyteMessage(
                    type=Type.LOG,
                    log=AirbyteLogMessage(level=Level.ERROR, message="oh no"),
                )
            ],
            True,
            True,
        ),
        ([], True, True),
        (
            [
                AirbyteMessage(
                    type=Type.TRACE,
                    trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=111, error=AirbyteErrorTraceMessage(message="oh no")),
                )
            ],
            False,
            False,
        ),
        (
            [
                AirbyteMessage(
                    type=Type.LOG,
                    log=AirbyteLogMessage(level=Level.ERROR, message="oh no"),
                )
            ],
            False,
            False,
        ),
        ([], False, False),
    ],
)
def test_airbyte_trace_message_on_failure(output, expect_trace_message_on_failure, should_fail):
    t = _TestBasicRead()
    input_config = BasicReadTestConfig(expect_trace_message_on_failure=expect_trace_message_on_failure)
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = output

    with patch.object(pytest, "skip", return_value=None):
        if should_fail:
            with pytest.raises(AssertionError, match="Connector should emit at least one error trace message"):
                t.test_airbyte_trace_message_on_failure(None, input_config, docker_runner_mock)
        else:
            t.test_airbyte_trace_message_on_failure(None, input_config, docker_runner_mock)


@pytest.mark.parametrize(
    "records, configured_catalog, expected_error",
    [
        (
            [AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111)],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {"name": "test1", "json_schema": {"type": "object", "properties": {"f1": {"type": "string"}}}}
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            "",
        ),
        (
            [AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111)],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {"type": "object", "properties": {"f1": {"type": "string"}, "f2": {"type": "string"}}},
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            r"`test1` stream has `\['/f2'\]`",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2"}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {"type": "object", "properties": {"f1": {"type": "string"}, "f2": {"type": "string"}}},
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": [1, 2, 3]}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {"type": "array", "items": {"type": "integer"}},
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": []}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {"type": "array", "items": {"type": "integer"}},
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            r"`test1` stream has `\['/f3/\[\]'\]`",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": {"f4": "v4", "f5": [1, 2]}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {"type": "object", "properties": {"f4": {"type": "string"}, "f5": {"type": "array"}}},
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": {"f4": "v4"}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {"type": "object", "properties": {"f4": {"type": "string"}, "f5": {"type": "array"}}},
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            r"`test1` stream has `\['/f3/f5/\[\]'\]`",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": {"f4": "v4"}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "type": "object",
                                            "properties": {
                                                "f4": {"type": "string"},
                                                "f5": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "f6": {"type": "string"},
                                                            "f7": {"type": "array"},
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            r"`test1` stream has `\['/f3/f5/\[\]/f6', '/f3/f5/\[\]/f7/\[\]'\]`",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(
                    stream="test1", data={"f2": "v2", "f3": {"f4": "v4", "f5": [{"f6": "v6", "f7": ["a", "b"]}]}}, emitted_at=111
                ),
                AirbyteRecordMessage(stream="test2", data={"f8": "v8"}, emitted_at=111),
                AirbyteRecordMessage(stream="test2", data={"f9": "v9"}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "type": "object",
                                            "properties": {
                                                "f4": {"type": "string"},
                                                "f5": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "f6": {"type": "string"},
                                                            "f7": {"type": "array"},
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test2",
                                "json_schema": {"type": "object", "properties": {"f8": {"type": "string"}, "f9": {"type": "string"}}},
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": {"f4": "v4", "f5": [{"f6": "v6", "f7": []}]}}, emitted_at=111),
                AirbyteRecordMessage(stream="test2", data={}, emitted_at=111),
                AirbyteRecordMessage(stream="test2", data={"f9": "v9"}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "type": "object",
                                            "properties": {
                                                "f4": {"type": "string"},
                                                "f5": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "f6": {"type": "string"},
                                                            "f7": {"type": "array"},
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test2",
                                "json_schema": {"type": "object", "properties": {"f8": {"type": "string"}, "f9": {"type": "string"}}},
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            r"(`test1` stream has `\['/f3/f5/\[\]/f7/\[\]']`)|(`test2` `\['/f8'\]`)",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1", "f2": "v2"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f3": {"f4": "v4"}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "oneOf": [
                                                {"type": "object", "properties": {"f4": {"type": "string"}}},
                                                {"type": "object", "properties": {"f5": {"type": "array"}}},
                                            ]
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1", "f2": "v2"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f3": {"f5": {"f7": "v7"}}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "oneOf": [
                                                {"type": "object", "properties": {"f4": {"type": "string"}}},
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "f5": {
                                                            "oneOf": [
                                                                {"type": "object", "properties": {"f6": {"type": "string"}}},
                                                                {"type": "object", "properties": {"f7": {"type": "string"}}},
                                                            ]
                                                        }
                                                    },
                                                },
                                            ]
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1", "f2": "v2"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f3": {"f5": {}}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "oneOf": [
                                                {"type": "object", "properties": {"f4": {"type": "string"}}},
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "f5": {
                                                            "anyOf": [
                                                                {"type": "object", "properties": {"f6": {"type": "string"}}},
                                                                {"type": "object", "properties": {"f7": {"type": "string"}}},
                                                            ]
                                                        }
                                                    },
                                                },
                                            ]
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            r"`test1` stream has `\['/f3\(0\)/f4', '/f3\(1\)/f5\(0\)/f6', '/f3\(1\)/f5\(1\)/f7'\]`",
        ),
    ],
)
def test_validate_field_appears_at_least_once(records, configured_catalog, expected_error):
    t = _TestBasicRead()
    if expected_error:
        with pytest.raises(AssertionError, match=expected_error):
            t._validate_field_appears_at_least_once(records=records, configured_catalog=configured_catalog)
    else:
        t._validate_field_appears_at_least_once(records=records, configured_catalog=configured_catalog)
