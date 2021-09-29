#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, Type
from source_acceptance_test.config import BasicReadTestConfig
from source_acceptance_test.tests.test_core import TestBasicRead as _TestBasicRead
from source_acceptance_test.tests.test_core import TestDiscovery as _TestDiscovery


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
            t.test_defined_cursors_exist_in_schema(None, discovered_catalog)
    else:
        t.test_defined_cursors_exist_in_schema(None, discovered_catalog)


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
