#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext as does_not_raise
from typing import Dict, List

import pytest
from _pytest.outcomes import Failed
from connector_acceptance_test.config import ConnectionTestConfig, IgnoredFieldsConfiguration
from connector_acceptance_test.tests.test_full_refresh import TestFullRefresh as _TestFullRefresh

from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    SyncMode,
    Type,
)


pytestmark = pytest.mark.anyio


class ReadTestConfigWithIgnoreFields(ConnectionTestConfig):
    ignored_fields: Dict[str, List[IgnoredFieldsConfiguration]] = {
        "test_stream": [
            IgnoredFieldsConfiguration(name="ignore_me", bypass_reason="test"),
            IgnoredFieldsConfiguration(name="ignore_me_too", bypass_reason="test"),
        ]
    }


def record_message_from_record(records: List[Dict], emitted_at: int) -> List[AirbyteMessage]:
    return [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=emitted_at),
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
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                **configured_catalog_kwargs,
            )
        ]
    )


fail_context = pytest.raises(
    Failed,
    match="the two sequential reads should produce either equal set of records or one of them is a strict subset of the other",
)
no_fail_context = does_not_raise()


recordset_comparison_test_cases = [
    pytest.param(
        [["id"]],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 1, "first_name": "Albert", "last_name": "Einstein"}, {"id": 2, "first_name": "Joseph", "last_name": "Lagrange"}],
        no_fail_context,
        id="pk_sets_equal_success",
    ),
    pytest.param(
        [["id"]],
        [
            {"id": 1, "first_name": "Thomas", "last_name": "Edison"},
        ],
        [{"id": 1, "first_name": "Albert", "last_name": "Einstein"}, {"id": 2, "first_name": "Joseph", "last_name": "Lagrange"}],
        no_fail_context,
        id="pk_first_is_subset_success",
    ),
    pytest.param(
        [["id"]],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 1, "first_name": "Albert", "last_name": "Einstein"}],
        fail_context,
        id="pk_second_is_subset_fail",
    ),
    pytest.param(
        [["id"]],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 2, "first_name": "Thomas", "last_name": "Edison"}, {"id": 3, "first_name": "Nicola", "last_name": "Tesla"}],
        fail_context,
        id="pk_no_subsets_fail",
    ),
    pytest.param(
        None,
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        no_fail_context,
        id="no_pk_sets_equal_success",
    ),
    pytest.param(
        None,
        [
            {"id": 1, "first_name": "Thomas", "last_name": "Edison"},
        ],
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        no_fail_context,
        id="no_pk_first_is_subset_success",
    ),
    pytest.param(
        None,
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [
            {"id": 1, "first_name": "Thomas", "last_name": "Edison"},
        ],
        fail_context,
        id="no_pk_second_is_subset_fail",
    ),
    pytest.param(
        None,
        [{"id": 1, "first_name": "Thomas", "last_name": "Edison"}, {"id": 2, "first_name": "Nicola", "last_name": "Tesla"}],
        [{"id": 2, "first_name": "Nicola", "last_name": "Tesla"}, {"id": 3, "first_name": "Albert", "last_name": "Einstein"}],
        fail_context,
        id="no_pk_no_subsets_fail",
    ),
]


@pytest.mark.parametrize(
    "schema, records_1, records_2, expectation",
    [
        (
            {"type": "object"},
            [
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 23}, emitted_at=111)),
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 24}, emitted_at=111)),
            ],
            [
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 23}, emitted_at=112)),
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 24}, emitted_at=112)),
            ],
            does_not_raise(),
        ),
        (
            {"type": "object"},
            [
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 23}, emitted_at=111)),
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 24}, emitted_at=111)),
            ],
            [
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 24}, emitted_at=112)),
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 23}, emitted_at=112)),
            ],
            does_not_raise(),
        ),
        (
            {"type": "object"},
            [
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 23}, emitted_at=111)),
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 24}, emitted_at=111)),
            ],
            [
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 23}, emitted_at=111)),
                AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"aa": 24}, emitted_at=112)),
            ],
            pytest.raises(AssertionError, match="emitted_at should increase on subsequent runs"),
        ),
    ],
)
async def test_emitted_at_increase_on_subsequent_runs(mocker, schema, records_1, records_2, expectation):
    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema, "supported_sync_modes": ["full_refresh"]}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
    docker_runner_mock = mocker.MagicMock(call_read=mocker.AsyncMock(side_effect=[records_1, records_2]))
    input_config = ReadTestConfigWithIgnoreFields()

    t = _TestFullRefresh()
    with expectation:
        await t.test_sequential_reads(
            ignored_fields=input_config.ignored_fields,
            connector_config=mocker.MagicMock(),
            configured_catalog=configured_catalog,
            docker_runner=docker_runner_mock,
            detailed_logger=docker_runner_mock,
        )
