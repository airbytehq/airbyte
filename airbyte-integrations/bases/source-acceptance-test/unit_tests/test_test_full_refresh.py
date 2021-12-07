from typing import Dict, List
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, AirbyteStream, AirbyteMessage, \
    AirbyteRecordMessage

from airbyte_protocol import Type
from source_acceptance_test.config import ConnectionTestConfig
from source_acceptance_test.tests.test_full_refresh import TestFullRefresh as _TestFullRefresh


class ReadTestConfigWithIgnoreFields(ConnectionTestConfig):
    ignored_fields: Dict[str, List[str]] = {"test_stream": ["ignore_me", "ignore_me_too"]}

@pytest.mark.parametrize(
    "schema, record, should_fail",
    [
        ({"type": "object"}, {"aa": 23}, False),
        ({"type": "object"}, {}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"aa": 23}, True),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"created": "23"}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}, "ignore_me": {"type": "string"}}}, {"created": "23"}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}, "DONT_ignore_me": {"type": "string"}}}, {"created": "23"}, True),
        # Recharge shop stream case
        (
            {"type": "object", "properties": {"shop": {"type": ["null", "object"]}, "store": {"type": ["null", "object"]}}},
            {"shop": {"a": "23"}, "store": {"b": "23"}},
            False,
        ),
    ],
)
def test_read_with_ignore_fields(schema, record, should_fail):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema, "supported_sync_modes": ["full_refresh"]}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",

            )
        ]
    )
    input_config = ReadTestConfigWithIgnoreFields()
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=111))
    ]
    t = _TestFullRefresh()
    if should_fail:
        with pytest.raises(AssertionError, match="stream should have some fields mentioned by json schema"):
            t.test_sequential_reads(inputs=input_config, connector_config=MagicMock(), configured_catalog=catalog, docker_runner=docker_runner_mock, detailed_logger=MagicMock())
    else:
        t.test_sequential_reads(inputs=input_config, connector_config=MagicMock(), configured_catalog=catalog, docker_runner=docker_runner_mock, detailed_logger=MagicMock())
