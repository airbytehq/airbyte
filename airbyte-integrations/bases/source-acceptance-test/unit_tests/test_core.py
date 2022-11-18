#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest import mock
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
    SyncMode,
    TraceType,
    Type,
)
from source_acceptance_test.config import BasicReadTestConfig, Config, ExpectedRecordsConfig
from source_acceptance_test.tests import test_core

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
    t = test_core.TestDiscovery()
    discovered_catalog = {
        "test_stream": AirbyteStream.parse_obj(
            {
                "name": "test_stream",
                "json_schema": schema,
                "default_cursor_field": cursors,
                "supported_sync_modes": ["full_refresh", "incremental"],
            }
        )
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
    t = test_core.TestDiscovery()
    discovered_catalog = {
        "test_stream": AirbyteStream.parse_obj(
            {"name": "test_stream", "json_schema": schema, "supported_sync_modes": ["full_refresh", "incremental"]}
        )
    }
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
    t = test_core.TestDiscovery()
    discovered_catalog = {
        "test_stream": AirbyteStream.parse_obj(
            {"name": "test_stream", "json_schema": schema, "supported_sync_modes": ["full_refresh", "incremental"]}
        )
    }
    if should_fail:
        with pytest.raises(AssertionError):
            t.test_defined_keyword_exist_in_schema(keyword, discovered_catalog)
    else:
        t.test_defined_keyword_exist_in_schema(keyword, discovered_catalog)


@pytest.mark.parametrize(
    "discovered_catalog, expectation",
    [
        ({"test_stream": mock.MagicMock(name="test_stream", json_schema={}, supported_sync_modes=None)}, pytest.raises(AssertionError)),
        (
            {"test_stream": mock.MagicMock(name="test_stream", json_schema={}, supported_sync_modes=[])},
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream": mock.MagicMock(
                    name="test_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
                )
            },
            does_not_raise(),
        ),
        (
            {"test_stream": mock.MagicMock(name="test_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])},
            does_not_raise(),
        ),
        (
            {"test_stream": mock.MagicMock(name="test_stream", json_schema={}, supported_sync_modes=[SyncMode.incremental])},
            does_not_raise(),
        ),
    ],
)
def test_supported_sync_modes_in_stream(mocker, discovered_catalog, expectation):
    t = test_core.TestDiscovery()
    with expectation:
        t.test_streams_has_sync_modes(discovered_catalog)


@pytest.mark.parametrize(
    "discovered_catalog, expectation",
    [
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {"name": "test_stream_1", "json_schema": {}, "supported_sync_modes": ["full_refresh"]}
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_2": AirbyteStream.parse_obj(
                    {"name": "test_stream_2", "json_schema": {"additionalProperties": True}, "supported_sync_modes": ["full_refresh"]}
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_3": AirbyteStream.parse_obj(
                    {"name": "test_stream_3", "json_schema": {"additionalProperties": False}, "supported_sync_modes": ["full_refresh"]}
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_4": AirbyteStream.parse_obj(
                    {"name": "test_stream_4", "json_schema": {"additionalProperties": "foo"}, "supported_sync_modes": ["full_refresh"]}
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_5": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_5",
                        "json_schema": {"additionalProperties": True, "properties": {"my_object": {"additionalProperties": True}}},
                        "supported_sync_modes": ["full_refresh"],
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
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
    ],
)
def test_additional_properties_is_true(discovered_catalog, expectation):
    t = test_core.TestDiscovery()
    with expectation:
        t.test_additional_properties_is_true(discovered_catalog)


@pytest.mark.parametrize(
    "test_strictness_level, configured_catalog_path",
    [
        (Config.TestStrictnessLevel.high, None),
        (Config.TestStrictnessLevel.high, "custom_configured_catalog_path"),
        (Config.TestStrictnessLevel.low, None),
        (Config.TestStrictnessLevel.low, "custom_configured_catalog_path"),
    ],
)
def test_configured_catalog_fixture(mocker, test_strictness_level, configured_catalog_path):
    mocker.patch.object(test_core, "build_configured_catalog_from_discovered_catalog_and_empty_streams")
    mocker.patch.object(test_core, "build_configured_catalog_from_custom_catalog")
    mocker.patch.object(test_core.pytest, "fail")

    mock_discovered_catalog = mocker.Mock()
    mock_empty_streams = mocker.Mock()
    t = test_core.TestBasicRead()
    configured_catalog = test_core.TestBasicRead.configured_catalog_fixture.__wrapped__(
        t, test_strictness_level, configured_catalog_path, mock_discovered_catalog, mock_empty_streams
    )
    if test_strictness_level is Config.TestStrictnessLevel.high:
        if configured_catalog_path:
            test_core.pytest.fail.assert_called_once()
        else:
            test_core.build_configured_catalog_from_discovered_catalog_and_empty_streams.assert_called_once_with(
                mock_discovered_catalog, mock_empty_streams
            )
            test_core.build_configured_catalog_from_custom_catalog.assert_not_called()
            assert configured_catalog == test_core.build_configured_catalog_from_discovered_catalog_and_empty_streams.return_value
    else:
        if configured_catalog_path is None:
            test_core.build_configured_catalog_from_discovered_catalog_and_empty_streams.assert_called_once_with(
                mock_discovered_catalog, mock_empty_streams
            )
            test_core.build_configured_catalog_from_custom_catalog.assert_not_called()
            assert configured_catalog == test_core.build_configured_catalog_from_discovered_catalog_and_empty_streams.return_value
        else:
            test_core.build_configured_catalog_from_custom_catalog.assert_called_once_with(configured_catalog_path, mock_discovered_catalog)
            test_core.build_configured_catalog_from_discovered_catalog_and_empty_streams.assert_not_called()
            assert configured_catalog == test_core.build_configured_catalog_from_custom_catalog.return_value


@pytest.mark.parametrize(
    "schema, record, expectation",
    [
        ({"type": "object"}, {"aa": 23}, does_not_raise()),
        ({"type": "object"}, {}, does_not_raise()),
        (
            {"type": "object", "properties": {"created": {"type": "string"}}},
            {"aa": 23},
            pytest.raises(AssertionError, match="should have some fields mentioned by json schema"),
        ),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"created": "23"}, does_not_raise()),
        (
            {"type": "object", "properties": {"created": {"type": "string"}}},
            {"root": {"created": "23"}},
            pytest.raises(AssertionError, match="should have some fields mentioned by json schema"),
        ),
        # Recharge shop stream case
        (
            {"type": "object", "properties": {"shop": {"type": ["null", "object"]}, "store": {"type": ["null", "object"]}}},
            {"shop": {"a": "23"}, "store": {"b": "23"}},
            does_not_raise(),
        ),
    ],
)
def test_read(schema, record, expectation):
    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema, "supported_sync_modes": ["full_refresh"]}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=111))
    ]
    t = test_core.TestBasicRead()
    with expectation:
        t.test_read(
            connector_config=None,
            configured_catalog=configured_catalog,
            expect_records_config=ExpectedRecordsConfig(path="foobar"),
            should_validate_schema=True,
            should_validate_data_points=False,
            empty_streams=set(),
            expected_records_by_stream={},
            docker_runner=docker_runner_mock,
            detailed_logger=MagicMock(),
        )


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
    t = test_core.TestBasicRead()
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
                            {
                                "name": "test1",
                                "json_schema": {"type": "object", "properties": {"f1": {"type": "string"}}},
                                "supported_sync_modes": ["full_refresh"],
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
            [AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111)],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {"type": "object", "properties": {"f1": {"type": "string"}, "f2": {"type": "string"}}},
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
                                "supported_sync_modes": ["full_refresh"],
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
    t = test_core.TestBasicRead()
    if expected_error:
        with pytest.raises(AssertionError, match=expected_error):
            t._validate_field_appears_at_least_once(records=records, configured_catalog=configured_catalog)
    else:
        t._validate_field_appears_at_least_once(records=records, configured_catalog=configured_catalog)
