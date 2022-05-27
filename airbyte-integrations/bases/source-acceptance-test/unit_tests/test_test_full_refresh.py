#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List
from unittest.mock import MagicMock

import pytest
from _pytest.outcomes import Failed
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, Type
from source_acceptance_test.config import ConnectionTestConfig
from source_acceptance_test.tests.test_full_refresh import TestFullRefresh as _TestFullRefresh


class ReadTestConfigWithIgnoreFields(ConnectionTestConfig):
    ignored_fields: Dict[str, List[str]] = {"test_stream": ["ignore_me", "ignore_me_too"]}


test_cases = [
    (
        {"type": "object", "properties": {"created": {"type": "string"}}},
        {"created": "23"},
        {"created": "23"},
        False,
        "no_ignored_fields_present",
    ),
    (
        {
            "type": "object",
            "properties": {
                "created": {"type": "string"},
                "ignore_me": {"type": "string"},
            },
        },
        {"created": "23"},
        {"created": "23", "ignore_me": "23"},
        False,
        "with_ignored_field",
    ),
    (
        {
            "type": "object",
            "required": ["created", "DONT_ignore_me"],
            "properties": {
                "created": {"type": "string"},
                "DONT_ignore_me": {"type": "string"},
                "ignore_me": {"type": "string"},
            },
        },
        {"created": "23"},
        {"created": "23", "DONT_ignore_me": "23", "ignore_me": "hello"},
        True,
        "ignore_field_present_but_a_required_is_not",
    ),
]


@pytest.mark.parametrize(
    "schema, record, expected_record, should_fail, test_case_name",
    test_cases,
    ids=[test_case[-1] for test_case in test_cases],
)
def test_read_with_ignore_fields(schema, record, expected_record, should_fail, test_case_name):
    catalog = get_default_catalog(schema)
    input_config = ReadTestConfigWithIgnoreFields()
    docker_runner_mock = MagicMock()

    def record_message_from_record(record_: Dict) -> List[AirbyteMessage]:
        return [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(stream="test_stream", data=record_, emitted_at=111),
            )
        ]

    sequence_of_docker_callread_results = [record, expected_record]

    # Ignored fields should work both ways
    for pair in (
        sequence_of_docker_callread_results,
        list(reversed(sequence_of_docker_callread_results)),
    ):
        docker_runner_mock.call_read.side_effect = [
            record_message_from_record(pair[0]),
            record_message_from_record(pair[1]),
        ]

        t = _TestFullRefresh()
        if should_fail:
            with pytest.raises(
                Failed,
                match="the two sequential reads should produce either equal set of records or one of them is a strict subset of the other",
            ):
                t.test_sequential_reads(
                    inputs=input_config,
                    connector_config=MagicMock(),
                    configured_catalog=catalog,
                    docker_runner=docker_runner_mock,
                    detailed_logger=MagicMock(),
                )
        else:
            t.test_sequential_reads(
                inputs=input_config,
                connector_config=MagicMock(),
                configured_catalog=catalog,
                docker_runner=docker_runner_mock,
                detailed_logger=MagicMock(),
            )


def get_default_catalog(schema):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream",
                    json_schema=schema,
                    supported_sync_modes=["full_refresh"],
                ),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
