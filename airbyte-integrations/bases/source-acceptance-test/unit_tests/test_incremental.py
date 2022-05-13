#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock

import pendulum
import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Type,
)
from source_acceptance_test.config import IncrementalConfig
from source_acceptance_test.tests.test_incremental import TestIncremental as _TestIncremental
from source_acceptance_test.tests.test_incremental import compare_cursor_with_threshold


def build_messages_from_record_data(records: list[dict]) -> list[AirbyteMessage]:
    return [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data=data, emitted_at=111)) for data in records
    ]


def build_state_message(state: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=state))


@pytest.mark.parametrize(
    "record_value, state_value, threshold_days, expected_result",
    [
        (datetime(2020, 10, 10), datetime(2020, 10, 9), 0, True),
        (datetime(2020, 10, 10), datetime(2020, 10, 11), 0, False),
        (datetime(2020, 10, 10), datetime(2020, 10, 11), 1, True),
        (pendulum.parse("2020-10-10"), pendulum.parse("2020-10-09"), 0, True),
        (pendulum.parse("2020-10-10"), pendulum.parse("2020-10-11"), 0, False),
        (pendulum.parse("2020-10-10"), pendulum.parse("2020-10-11"), 1, True),
        ("2020-10-10", "2020-10-09", 0, True),
        ("2020-10-10", "2020-10-11", 0, False),
        ("2020-10-10", "2020-10-11", 1, True),
        (1602288000000, 1602201600000, 0, True),
        (1602288000000, 1602374400000, 0, False),
        (1602288000000, 1602374400000, 1, True),
        (1602288000, 1602201600, 0, True),
        (1602288000, 1602374400, 0, False),
        (1602288000, 1602374400, 1, True),
        ("aaa", "bbb", 0, False),
        ("bbb", "aaa", 0, True),
    ],
)
def test_compare_cursor_with_threshold(record_value, state_value, threshold_days, expected_result):
    assert compare_cursor_with_threshold(record_value, state_value, threshold_days) == expected_result


@pytest.mark.parametrize("cursor_type", ["date", "string"])
@pytest.mark.parametrize(
    "records1, records2, latest_state, threshold_days, expected_error",
    [
        ([{"date": "2020-01-01"}, {"date": "2020-01-02"}], [], "2020-01-02", 0, None),
        ([{"date": "2020-01-02"}, {"date": "2020-01-03"}], [], "2020-01-02", 0, "First incremental sync should produce records younger"),
        ([{"date": "2020-01-01"}, {"date": "2020-01-02"}], [{"date": "2020-01-02"}, {"date": "2020-01-03"}], "2020-01-02", 0, None),
        ([{"date": "2020-01-01"}], [{"date": "2020-01-01"}], "2020-01-02", 0, "Second incremental sync should produce records older"),
        ([{"date": "2020-01-01"}, {"date": "2020-01-02"}], [{"date": "2020-01-01"}, {"date": "2020-01-02"}], "2020-01-03", 2, None),
        ([{"date": "2020-01-02"}, {"date": "2020-01-03"}], [], "2020-01-02", 2, "First incremental sync should produce records younger"),
        ([{"date": "2020-01-01"}], [{"date": "2020-01-02"}], "2020-01-06", 3, "Second incremental sync should produce records older"),
    ],
)
def test_incremental_two_sequential_reads(records1, records2, latest_state, threshold_days, cursor_type, expected_error):
    input_config = IncrementalConfig(threshold_days=threshold_days)
    cursor_paths = {"test_stream": ["date"]}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream",
                    json_schema={"type": "object", "properties": {"date": {"type": cursor_type}}},
                    supported_sync_modes=["full_refresh", "incremental"],
                ),
                sync_mode="incremental",
                destination_sync_mode="overwrite",
                cursor_field=["date"],
            )
        ]
    )

    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = [*build_messages_from_record_data(records1), build_state_message({"date": latest_state})]
    docker_runner_mock.call_read_with_state.return_value = build_messages_from_record_data(records2)

    t = _TestIncremental()
    if expected_error:
        with pytest.raises(AssertionError, match=expected_error):
            t.test_two_sequential_reads(
                inputs=input_config,
                connector_config=MagicMock(),
                configured_catalog_for_incremental=catalog,
                cursor_paths=cursor_paths,
                docker_runner=docker_runner_mock,
            )
    else:
        t.test_two_sequential_reads(
            inputs=input_config,
            connector_config=MagicMock(),
            configured_catalog_for_incremental=catalog,
            cursor_paths=cursor_paths,
            docker_runner=docker_runner_mock,
        )
