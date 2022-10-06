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


def record_message_from_record(records: List[Dict]) -> List[AirbyteMessage]:
    return [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=111),
        )
        for record in records
    ]


def get_default_catalog(schema, **kwargs):
    configured_catalog_kwargs = {"sync_mode": "full_refresh", "destination_sync_mode": "overwrite"}
    primary_key = kwargs.get("primary_key")
    if primary_key:
        configured_catalog_kwargs["primary_key"] = primary_key
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream",
                    json_schema=schema,
                    supported_sync_modes=["full_refresh"],
                ),
                **configured_catalog_kwargs,
            )
        ]
    )


ignored_fields_test_cases = [
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
    ignored_fields_test_cases,
    ids=[test_case[-1] for test_case in ignored_fields_test_cases],
)
def test_read_with_ignore_fields(schema, record, expected_record, should_fail, test_case_name):
    catalog = get_default_catalog(schema)
    input_config = ReadTestConfigWithIgnoreFields()
    docker_runner_mock = MagicMock()

    sequence_of_docker_callread_results = [record, expected_record]

    # Ignored fields should work both ways
    for first, second in (
        sequence_of_docker_callread_results,
        list(reversed(sequence_of_docker_callread_results)),
    ):
        docker_runner_mock.call_read.side_effect = [record_message_from_record([first]), record_message_from_record([second])]

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


recordset_comparison_test_cases = [
    (
        [["id"]],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 1, "first_name": "Albert", "last_name": "Einstein"}, {"id": 2, "first_name": "Joseph", "last_name": "Lagrange"}],
        False,
        "pk_sets_equal_success",
    ),
    (
        [["id"]],
        [
            {"id": 1, "first_name": "Thomas", "last_name": "Edison"},
        ],
        [{"id": 1, "first_name": "Albert", "last_name": "Einstein"}, {"id": 2, "first_name": "Joseph", "last_name": "Lagrange"}],
        False,
        "pk_first_is_subset_success",
    ),
    (
        [["id"]],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 1, "first_name": "Albert", "last_name": "Einstein"}],
        True,
        "pk_second_is_subset_fail",
    ),
    (
        [["id"]],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 2, "first_name": "Thomas", "last_name": "Edison"}, {"id": 3, "first_name": "Nicola", "last_name": "Tesla"}],
        True,
        "pk_no_subsets_fail",
    ),
    (
        None,
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        False,
        "no_pk_sets_equal_success",
    ),
    (
        None,
        [
            {"id": 1, "first_name": "Thomas", "last_name": "Edison"},
        ],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        False,
        "no_pk_first_is_subset_success",
    ),
    (
        None,
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [
            {"id": 1, "first_name": "Thomas", "last_name": "Edison"},
        ],
        True,
        "no_pk_second_is_subset_fail",
    ),
    (
        None,
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 2, "first_name": "Nicola", "last_name": "Tesla"}, {"id": 3, "first_name": "Albert", "last_name": "Einstein"}],
        True,
        "no_pk_no_subsets_fail",
    ),
]


@pytest.mark.parametrize(
    "primary_key, first_read_records, second_read_records, should_fail, test_case_name",
    recordset_comparison_test_cases,
    ids=[test_case[-1] for test_case in recordset_comparison_test_cases],
)
def test_recordset_comparison(primary_key, first_read_records, second_read_records, should_fail, test_case_name):
    schema = {
        "type": "object",
        "properties": {"id": {"type": "integer"}, "first_name": {"type": "string"}, "last_name": {"type": "string"}},
    }
    catalog = get_default_catalog(schema, primary_key=primary_key)
    input_config = ReadTestConfigWithIgnoreFields()
    docker_runner_mock = MagicMock()

    docker_runner_mock.call_read.side_effect = [
        record_message_from_record(first_read_records),
        record_message_from_record(second_read_records),
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
