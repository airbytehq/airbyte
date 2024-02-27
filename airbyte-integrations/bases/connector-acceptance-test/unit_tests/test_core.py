#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from _pytest.outcomes import Failed
from airbyte_protocol.models import (
    AirbyteErrorTraceMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Level,
    StreamDescriptor,
    SyncMode,
    TraceType,
    Type,
)
from connector_acceptance_test.config import (
    BasicReadTestConfig,
    Config,
    ExpectedRecordsConfig,
    FileTypesConfig,
    IgnoredFieldsConfiguration,
    UnsupportedFileTypeConfig,
)
from connector_acceptance_test.tests import test_core
from jsonschema.exceptions import SchemaError

from .conftest import does_not_raise

pytestmark = pytest.mark.anyio


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


def test_discovery_uniquely_named_streams():
    t = test_core.TestDiscovery()
    stream_a = AirbyteStream.parse_obj(
        {
            "name": "test_stream",
            "json_schema": {"properties": {"created": {"type": "string"}}},
            "default_cursor_field": ["created"],
            "supported_sync_modes": ["full_refresh", "incremental"],
        }
    )
    streams = [stream_a, stream_a]
    assert t.duplicated_stream_names(streams) == ["test_stream"]
    streams.pop()
    assert len(t.duplicated_stream_names(streams)) == 0


@pytest.mark.parametrize(
    "schema, should_fail",
    [
        (
            {
                "$schema": "https://json-schema.org/draft-07/schema#",
                "type": ["null", "object"],
                "properties": {
                    "amount": {
                        "type": ["null", "integer"]
                    },
                    "amount_details": {
                        "type": ["null", "object"],
                        "properties": {
                            "atm_fee": ["null", "integer"]
                        }
                    }
                }
            },
            True
        ),
        (
            {
                "$schema": "https://json-schema.org/draft-07/schema#",
                "type": ["null", "object"],
                "properties": {
                    "amount": "integer",
                    "amount_details": {
                        "type": ["null", "object"],
                        "properties": {
                            "atm_fee": {
                                "type": ["null", "integer"]
                            }
                        }
                    }
                }
            },
            True
        ),
        (
            {
                "$schema": "https://json-schema.org/draft-07/schema#",
                "type": ["null", "object"],
                "properties": {
                    "amount": {
                        "type": ["null", "integer"]
                    },
                    "amount_details": {
                        "type": ["null", "object"],
                        "properties": {
                            "atm_fee": {
                                "type": ["null", "integer"]
                            }
                        }
                    }
                }
            },
            False
        )
    ],
)
def test_streams_have_valid_json_schemas(schema, should_fail):
    t = test_core.TestDiscovery()
    discovered_catalog = {
        "test_stream": AirbyteStream.parse_obj(
            {
                "name": "test_stream",
                "json_schema": schema,
                "supported_sync_modes": ["full_refresh", "incremental"],
            }
        )
    }
    expectation = pytest.raises(SchemaError) if should_fail else does_not_raise()
    with expectation:
        t.test_streams_have_valid_json_schemas(discovered_catalog)


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
    "discovered_catalog, expectation",
    [
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": "string"}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": ["null", "string"]}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"user": {"type": "object", "properties": {"name": {"type": "string"}}}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": "unsupported"}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": ["null", "unsupported"]}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": "string", "format": "date"}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": "string", "format": "date-time"}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": "string", "format": "datetime"}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": "number", "format": "date"}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": "string", "format": "date", "airbyte_type": "unsupported"}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"username": {"type": "number", "airbyte_type": "timestamp_with_timezone"}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {
                            "properties": {"user": {"type": "object", "properties": {"name": {"type": "string", "format": "unsupported"}}}}
                        },
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {
                            "properties": {
                                "user": {"type": "object", "properties": {"name with space": {"type": "string", "format": "unsupported"}}}
                            }
                        },
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            pytest.raises(AssertionError),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"type": {"type": ["string"]}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"with/slash": {"type": ["string"]}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            does_not_raise(),
        ),
        (
            {
                "test_stream_1": AirbyteStream.parse_obj(
                    {
                        "name": "test_stream_1",
                        "json_schema": {"properties": {"with space": {"type": ["string"]}}},
                        "supported_sync_modes": ["full_refresh"],
                    }
                )
            },
            does_not_raise(),
        ),
    ],
)
def test_catalog_has_supported_data_types(discovered_catalog, expectation):
    t = test_core.TestDiscovery()
    with expectation:
        t.test_catalog_has_supported_data_types(discovered_catalog)


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


_DEFAULT_RECORD_CONFIG = ExpectedRecordsConfig(path="foobar")


@pytest.mark.parametrize(
    "schema, ignored_fields, expect_records_config, record, expected_records_by_stream, primary_key, expectation",
    [
        ({"type": "object"}, {}, _DEFAULT_RECORD_CONFIG, {"aa": 23}, {}, None, does_not_raise()),
        ({"type": "object"}, {}, _DEFAULT_RECORD_CONFIG, {}, {}, None, does_not_raise()),
        (
            {"type": "object", "properties": {"created": {"type": "string"}}},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"aa": 23},
            {},
            None,
            pytest.raises(AssertionError, match="should have some fields mentioned by json schema"),
        ),
        (
            {"type": "object", "properties": {"created": {"type": "string"}}},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"created": "23"},
            {},
            None,
            does_not_raise(),
        ),
        (
            {"type": "object", "properties": {"created": {"type": "string"}}},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"root": {"created": "23"}},
            {},
            None,
            pytest.raises(AssertionError, match="should have some fields mentioned by json schema"),
        ),
        # Recharge shop stream case
        (
            {"type": "object", "properties": {"shop": {"type": ["null", "object"]}, "store": {"type": ["null", "object"]}}},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"shop": {"a": "23"}, "store": {"b": "23"}},
            {},
            None,
            does_not_raise(),
        ),
        # Fail when expected and actual records are not equal
        (
            {"type": "object"},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"constant_field": "must equal", "fast_changing_field": [{"field": 2}]},
            {"test_stream": [{"constant_field": "must equal", "fast_changing_field": [{"field": 1}]}]},
            None,
            pytest.raises(Failed, match="Stream test_stream: All expected records must be produced"),
        ),
        # Expected and Actual records are not equal but we ignore fast changing field
        (
            {"type": "object"},
            {"test_stream": [IgnoredFieldsConfiguration(name="fast_changing_field/*/field", bypass_reason="test")]},
            _DEFAULT_RECORD_CONFIG,
            {"constant_field": "must equal", "fast_changing_field": [{"field": 2}]},
            {"test_stream": [{"constant_field": "must equal", "fast_changing_field": [{"field": 1}]}]},
            None,
            does_not_raise(),
        ),
        # Fail when expected and actual records are not equal and exact_order=True
        (
            {"type": "object"},
            {},
            ExpectedRecordsConfig(extra_fields=False, exact_order=True, extra_records=True, path="foobar"),
            {"constant_field": "must equal", "fast_changing_field": [{"field": 2}]},
            {"test_stream": [{"constant_field": "must equal", "fast_changing_field": [{"field": 1}]}]},
            None,
            pytest.raises(AssertionError, match="Stream test_stream: Mismatch of record order or values"),
        ),
        # Expected and Actual records are not equal but we ignore fast changing field (for case when exact_order=True)
        (
            {"type": "object"},
            {"test_stream": [IgnoredFieldsConfiguration(name="fast_changing_field/*/field", bypass_reason="test")]},
            ExpectedRecordsConfig(extra_fields=False, exact_order=True, extra_records=True, path="foobar"),
            {"constant_field": "must equal", "fast_changing_field": [{"field": 1}]},
            {"test_stream": [{"constant_field": "must equal", "fast_changing_field": [{"field": 2}]}]},
            None,
            does_not_raise(),
        ),
        # Match by primary key
        (
            {"type": "object"},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"primary_key": "a primary_key"},
            {"test_stream": [{"primary_key": "a primary_key"}]},
            [["primary_key"]],
            does_not_raise(),
        ),
        # Match by primary key when actual has added fields
        (
            {"type": "object"},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"primary_key": "a primary_key", "a field that should be ignored": "ignored value"},
            {"test_stream": [{"primary_key": "a primary_key"}]},
            [["primary_key"]],
            does_not_raise(),
        ),
        # Match by primary key when non primary key field values differ
        (
            {"type": "object"},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"primary_key": "a primary_key", "matching key": "value 1"},
            {"test_stream": [{"primary_key": "a primary_key", "non matching key": "value 2"}]},
            [["primary_key"]],
            does_not_raise(),
        ),
        # Match nested primary key
        (
            {"type": "object"},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"top_level_field": {"child_field": "a primary_key"}, "matching key": "value 1"},
            {"test_stream": [{"top_level_field": {"child_field": "a primary_key"}, "matching key": "value 1"}]},
            [["top_level_field", "child_field"]],
            does_not_raise(),
        ),
        # Match composite primary key
        (
            {"type": "object"},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"primary_key_1": "a primary_key_1", "primary_key_2": "a primary_key_2"},
            {"test_stream": [{"primary_key_1": "a primary_key_1", "primary_key_2": "a primary_key_2"}]},
            [["primary_key_1"], ["primary_key_2"]],
            does_not_raise(),
        ),
        # Match composite and nested primary key
        (
            {"type": "object"},
            {},
            _DEFAULT_RECORD_CONFIG,
            {"primary_key_1": "a primary_key_1", "primary_key_2_1": {"primary_key_2_2": "primary_key_2"}},
            {"test_stream": [{"primary_key_1": "a primary_key_1", "primary_key_2_1": {"primary_key_2_2": "primary_key_2"}}]},
            [["primary_key_1"], ["primary_key_2_1", "primary_key_2_2"]],
            does_not_raise(),
        ),
    ],
)
async def test_read(mocker, schema, ignored_fields, expect_records_config, record, expected_records_by_stream, primary_key, expectation):
    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({
                    "name": "test_stream",
                    "json_schema": schema,
                    "supported_sync_modes": ["full_refresh"],
                    "source_defined_primary_key": primary_key
                }),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
    docker_runner_mock = mocker.MagicMock(
        call_read=mocker.AsyncMock(
            return_value=[AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=111))]
        )
    )
    t = test_core.TestBasicRead()
    with expectation:
        await t.test_read(
            connector_config=None,
            configured_catalog=configured_catalog,
            expect_records_config=expect_records_config,
            should_validate_schema=True,
            should_validate_data_points=False,
            should_validate_stream_statuses=False,
            should_fail_on_extra_columns=False,
            empty_streams=set(),
            expected_records_by_stream=expected_records_by_stream,
            docker_runner=docker_runner_mock,
            ignored_fields=ignored_fields,
            detailed_logger=MagicMock(),
            certified_file_based_connector=False,
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
async def test_airbyte_trace_message_on_failure(mocker, output, expect_trace_message_on_failure, should_fail):
    t = test_core.TestBasicRead()
    input_config = BasicReadTestConfig(expect_trace_message_on_failure=expect_trace_message_on_failure)
    docker_runner_mock = mocker.MagicMock(call_read=mocker.AsyncMock(return_value=output))

    with patch.object(pytest, "skip", return_value=None):
        if should_fail:
            with pytest.raises(AssertionError, match="Connector should emit at least one error trace message"):
                await t.test_airbyte_trace_message_on_failure(None, input_config, docker_runner_mock)
        else:
            await t.test_airbyte_trace_message_on_failure(None, input_config, docker_runner_mock)


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


async def test_read_validate_async_output_stream_statuses(mocker):
    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": f"test_stream_{x}", "json_schema": {}, "supported_sync_modes": ["full_refresh"]}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
            for x in range(3)
        ]
    )
    async_stream_output = [
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_0"), status=AirbyteStreamStatus.STARTED
                ),
            ),
        ),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_2"), status=AirbyteStreamStatus.STARTED
                ),
            ),
        ),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_1"), status=AirbyteStreamStatus.STARTED
                ),
            ),
        ),
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream_0", data={"a": 1}, emitted_at=111)),
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream_1", data={"a": 1}, emitted_at=112)),
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream_2", data={"a": 1}, emitted_at=113)),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=114,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_1"), status=AirbyteStreamStatus.RUNNING
                ),
            ),
        ),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=114,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_2"), status=AirbyteStreamStatus.RUNNING
                ),
            ),
        ),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=114,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_0"), status=AirbyteStreamStatus.RUNNING
                ),
            ),
        ),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=115,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_1"), status=AirbyteStreamStatus.RUNNING
                ),
            ),
        ),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=115,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_2"), status=AirbyteStreamStatus.COMPLETE
                ),
            ),
        ),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=116,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_1"), status=AirbyteStreamStatus.COMPLETE
                ),
            ),
        ),
        AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=120,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="test_stream_0"), status=AirbyteStreamStatus.COMPLETE
                ),
            ),
        ),
    ]
    docker_runner_mock = mocker.MagicMock(call_read=mocker.AsyncMock(return_value=async_stream_output))

    t = test_core.TestBasicRead()
    await t.test_read(
        connector_config=None,
        configured_catalog=configured_catalog,
        expect_records_config=_DEFAULT_RECORD_CONFIG,
        should_validate_schema=False,
        should_validate_data_points=False,
        should_validate_stream_statuses=True,
        should_fail_on_extra_columns=False,
        empty_streams=set(),
        expected_records_by_stream={},
        docker_runner=docker_runner_mock,
        ignored_fields=None,
        detailed_logger=MagicMock(),
        certified_file_based_connector=False,
    )


@pytest.mark.parametrize(
    "output",
    [
        (AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream_0", data={"a": 1}, emitted_at=111)),),
        (
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=1,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name="test_stream_0"), status=AirbyteStreamStatus.STARTED
                    ),
                ),
            ),
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream_0", data={"a": 1}, emitted_at=111)),
        ),
        (
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=1,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name="test_stream_0"), status=AirbyteStreamStatus.STARTED
                    ),
                ),
            ),
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream_0", data={"a": 1}, emitted_at=111)),
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=2,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name="test_stream_0"), status=AirbyteStreamStatus.RUNNING
                    ),
                ),
            ),
        ),
        (
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream_0", data={"a": 1}, emitted_at=111)),
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=2,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name="test_stream_0"), status=AirbyteStreamStatus.RUNNING
                    ),
                ),
            ),
        ),
        (
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream_0", data={"a": 1}, emitted_at=111)),
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=2,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name="test_stream_0"), status=AirbyteStreamStatus.COMPLETE
                    ),
                ),
            ),
        ),
    ],
    ids=["no_statuses", "only_started_present", "only_started_and_running_present", "only_running", "only_complete"],
)
async def test_read_validate_stream_statuses_exceptions(mocker, output):
    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": f"test_stream_0", "json_schema": {}, "supported_sync_modes": ["full_refresh"]}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
    docker_runner_mock = mocker.MagicMock(call_read=mocker.AsyncMock(return_value=output))

    t = test_core.TestBasicRead()
    with pytest.raises(AssertionError):
        await t.test_read(
            connector_config=None,
            configured_catalog=configured_catalog,
            expect_records_config=_DEFAULT_RECORD_CONFIG,
            should_validate_schema=False,
            should_validate_data_points=False,
            should_validate_stream_statuses=True,
            should_fail_on_extra_columns=False,
            empty_streams=set(),
            expected_records_by_stream={},
            docker_runner=docker_runner_mock,
            ignored_fields=None,
            detailed_logger=MagicMock(),
            certified_file_based_connector=False,
        )


@pytest.mark.parametrize(
    "metadata, expected_file_based, is_connector_certified",
    [
        ({"data": {"connectorSubtype": "file", "ab_internal": {"ql": 400}}}, True, True),
        ({"data": {"connectorSubtype": "file", "ab_internal": {"ql": 500}}}, True, True),
        ({}, False, False),
        ({"data": {"ab_internal": {}}}, False, False),
        ({"data": {"ab_internal": {"ql": 400}}}, False, False),
        ({"data": {"connectorSubtype": "file"}}, False, False),
        ({"data": {"connectorSubtype": "file", "ab_internal": {"ql": 200}}}, False, False),
        ({"data": {"connectorSubtype": "not_file", "ab_internal": {"ql": 400}}}, False, False),
    ],
)
def test_is_certified_file_based_connector(metadata, is_connector_certified, expected_file_based):
    t = test_core.TestBasicRead()
    assert test_core.TestBasicRead.is_certified_file_based_connector.__wrapped__(t, metadata, is_connector_certified) is expected_file_based


@pytest.mark.parametrize(
    ("file_name", "expected_extension"),
    (
        ("test.csv", ".csv"),
        ("test/directory/test.csv", ".csv"),
        ("test/directory/test.CSV", ".csv"),
        ("test/directory/", ""),
        (".bashrc", ""),
        ("", ""),
    ),
)
def test_get_file_extension(file_name, expected_extension):
    t = test_core.TestBasicRead()
    assert t._get_file_extension(file_name) == expected_extension


@pytest.mark.parametrize(
    ("records", "expected_file_types"),
    (
        ([], set()),
        (
            [
                AirbyteRecordMessage(stream="stream", data={"field": "value", "_ab_source_file_url": "test.csv"}, emitted_at=111),
                AirbyteRecordMessage(stream="stream", data={"field": "value", "_ab_source_file_url": "test_2.pdf"}, emitted_at=111),
                AirbyteRecordMessage(stream="stream", data={"field": "value", "_ab_source_file_url": "test_3.pdf"}, emitted_at=111),
                AirbyteRecordMessage(stream="stream", data={"field": "value", "_ab_source_file_url": "test_3.CSV"}, emitted_at=111),
            ],
            {".csv", ".pdf"},
        ),
        (
            [
                AirbyteRecordMessage(stream="stream", data={"field": "value"}, emitted_at=111),
                AirbyteRecordMessage(stream="stream", data={"field": "value", "_ab_source_file_url": ""}, emitted_at=111),
                AirbyteRecordMessage(stream="stream", data={"field": "value", "_ab_source_file_url": ".bashrc"}, emitted_at=111),
            ],
            {""},
        ),
    ),
)
def test_get_actual_file_types(records, expected_file_types):
    t = test_core.TestBasicRead()
    assert t._get_actual_file_types(records) == expected_file_types


@pytest.mark.parametrize(
    ("config", "expected_file_types"),
    (
        ([], set()),
        ([UnsupportedFileTypeConfig(extension=".csv"), UnsupportedFileTypeConfig(extension=".pdf")], {".csv", ".pdf"}),
        ([UnsupportedFileTypeConfig(extension=".CSV")], {".csv"}),
    ),
)
def test_get_unsupported_file_types(config, expected_file_types):
    t = test_core.TestBasicRead()
    assert t._get_unsupported_file_types(config) == expected_file_types


@pytest.mark.parametrize(
    ("is_file_based_connector", "skip_test"),
    ((False, True), (False, False), (True, True)),
)
async def test_all_supported_file_types_present_skipped(mocker, is_file_based_connector, skip_test):
    mocker.patch.object(test_core.pytest, "skip")
    mocker.patch.object(test_core.TestBasicRead, "_file_types", {".avro", ".csv", ".jsonl", ".parquet", ".pdf"})

    t = test_core.TestBasicRead()
    config = BasicReadTestConfig(config_path="config_path", file_types=FileTypesConfig(skip_test=skip_test))
    await t.test_all_supported_file_types_present(is_file_based_connector, config)
    test_core.pytest.skip.assert_called_once()


@pytest.mark.parametrize(
    ("file_types_found", "should_fail"),
    (
        ({".avro", ".csv", ".jsonl", ".parquet", ".pdf"}, False),
        ({".csv", ".jsonl", ".parquet", ".pdf"}, True),
        ({".avro", ".csv", ".jsonl", ".parquet"}, True),
    ),
)
async def test_all_supported_file_types_present(mocker, file_types_found, should_fail):
    mocker.patch.object(test_core.TestBasicRead, "_file_types", file_types_found)
    t = test_core.TestBasicRead()
    config = BasicReadTestConfig(config_path="config_path", file_types=FileTypesConfig(skip_test=False))

    if should_fail:
        with pytest.raises(AssertionError) as e:
            await t.test_all_supported_file_types_present(certified_file_based_connector=True, inputs=config)
    else:
        await t.test_all_supported_file_types_present(certified_file_based_connector=True, inputs=config)
