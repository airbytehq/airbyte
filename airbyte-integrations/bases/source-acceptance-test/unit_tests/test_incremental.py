#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock, patch

import pendulum
import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from source_acceptance_test.config import IncrementalConfig
from source_acceptance_test.tests.test_incremental import TestIncremental as _TestIncremental
from source_acceptance_test.tests.test_incremental import compare_cursor_with_threshold


def build_messages_from_record_data(stream: str, records: list[dict]) -> list[AirbyteMessage]:
    return [build_record_message(stream, data) for data in records]


def build_record_message(stream: str, data: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=111))


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
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.overwrite,
                cursor_field=["date"],
            )
        ]
    )

    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = [
        *build_messages_from_record_data("test_stream", records1),
        build_state_message({"date": latest_state}),
    ]
    docker_runner_mock.call_read_with_state.return_value = build_messages_from_record_data("test_stream", records2)

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


@pytest.mark.parametrize(
    "test_name, records, state_records, threshold_days, expected_error",
    [
        (
            "test_incremental_with_2_states",
            [
                build_state_message(state={}),
                # *build_messages_from_record_data(stream="test_stream", records=[{"date": "2022-05-07"}]),
                build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                build_record_message(stream="test_stream", data={"date": "2022-05-09"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-10"}),
                build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                build_record_message(stream="test_stream", data={"date": "2022-05-11"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
            ],
            [
                [
                    build_state_message(state={}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-09"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-10"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-09"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-10"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
                ],
            ],
            0,
            None,
        ),
        (
            "test_first_incremental_only_younger_records",
            [
                build_state_message(state={}),
                build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-13"}),
                build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
            ],
            [
                [
                    build_state_message(state={}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-13"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-13"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                ],
                [build_state_message(state={"test_stream": {"date": "2022-05-11"}})],
            ],
            0,
            AssertionError,
        ),
        (
            "test_incremental_with_threshold",
            [
                build_state_message(state={}),
                build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
            ],
            [
                [
                    build_state_message(state={}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                ],
                [build_state_message(state={"test_stream": {"date": "2022-05-11"}})],
            ],
            3,
            None,
        ),
        (
            "test_incremental_with_incorrect_messages",
            [
                build_state_message(state={}),
                build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                build_record_message(stream="test_stream", data={"date": "2022-05-04"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-05"}),
                build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                build_record_message(stream="test_stream", data={"date": "2022-05-11"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
            ],
            [
                [
                    build_state_message(state={}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-04"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-05"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-04"}),  # out of order
                    build_record_message(stream="test_stream", data={"date": "2022-05-05"}),  # out of order
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-13"}}),
                ],
                [build_state_message(state={"test_stream": {"date": "2022-05-13"}})],
            ],
            0,
            AssertionError,
        ),
        (
            "test_incremental_with_multiple_streams",
            [
                build_state_message(state={}),
                build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                build_record_message(stream="test_stream", data={"date": "2022-05-09"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-10"}),
                build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                build_record_message(stream="test_stream_2", data={"date": "2022-05-11"}),
                build_record_message(stream="test_stream_2", data={"date": "2022-05-12"}),
                build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}}),
                build_record_message(stream="test_stream_2", data={"date": "2022-05-13"}),
                build_record_message(stream="test_stream_2", data={"date": "2022-05-14"}),
                build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}}),
            ],
            [
                [
                    build_state_message(state={}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-09"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-10"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-13"}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-14"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-09"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-10"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-13"}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-14"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-11"}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-12"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-13"}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-14"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-13"}),
                    build_record_message(stream="test_stream_2", data={"date": "2022-05-14"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}}),
                ],
                [
                    build_state_message(state={"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}}),
                ],
            ],
            0,
            None,
        ),
        (
            "test_incremental_with_none_state",
            [
                build_state_message(state={"test_stream": None}),
                build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
            ],
            [
                [
                    build_state_message(state={"test_stream": None}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-07"}),
                    build_record_message(stream="test_stream", data={"date": "2022-05-08"}),
                    build_state_message(state={"test_stream": {"date": "2022-05-09"}}),
                ],
                [],
            ],
            0,
            None,
        ),
    ],
)
def test_read_with_multiple_states(test_name, records, state_records, threshold_days, expected_error):
    input_config = IncrementalConfig(threshold_days=threshold_days)
    cursor_paths = {"test_stream": ["date"]}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream",
                    json_schema={"type": "object", "properties": {"date": {"type": "date"}}},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.overwrite,
                cursor_field=["date"],
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream_2",
                    json_schema={"type": "object", "properties": {"date": {"type": "date"}}},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.overwrite,
                cursor_field=["date"],
            ),
        ]
    )

    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = records
    docker_runner_mock.call_read_with_state.side_effect = state_records

    t = _TestIncremental()
    if expected_error:
        with pytest.raises(expected_error):
            t.test_read_sequential_slices(
                inputs=input_config,
                connector_config=MagicMock(),
                configured_catalog_for_incremental=catalog,
                cursor_paths=cursor_paths,
                docker_runner=docker_runner_mock,
            )
    else:
        t.test_read_sequential_slices(
            inputs=input_config,
            connector_config=MagicMock(),
            configured_catalog_for_incremental=catalog,
            cursor_paths=cursor_paths,
            docker_runner=docker_runner_mock,
        )


def test_config_skip_test():
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = []
    t = _TestIncremental()
    with patch.object(pytest, "skip", return_value=None):
        t.test_read_sequential_slices(
            inputs=IncrementalConfig(skip_comprehensive_incremental_tests=True),
            connector_config=MagicMock(),
            configured_catalog_for_incremental=ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream(
                            name="test_stream",
                            json_schema={"type": "object", "properties": {"date": {"type": "date"}}},
                            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                        ),
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.overwrite,
                        cursor_field=["date"],
                    )
                ]
            ),
            cursor_paths={},
            docker_runner=docker_runner_mock,
        )

    # This is guaranteed to fail when the test gets executed
    docker_runner_mock.call_read.assert_not_called()
