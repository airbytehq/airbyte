# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .helpers import PAGE_SIZE, START_DATE_PARAM, json_response, read_stream, request


_INCREMENTAL_STREAMS = [
    ("orders", "orderId", "modifyDate", "modifyDateStart", {"sortBy": "ModifyDate", "sortDir": "ASC"}),
    ("shipments", "shipmentId", "createDate", "createDateStart", {"sortBy": "CreateDate", "sortDir": "ASC", "includeShipmentItems": "true"}),
    ("fulfillments", "fulfillmentId", "createDate", "createDateStart", {"sortBy": "CreateDate", "sortDir": "ASC"}),
]


def _page_one(stream_name: str, base_params: Dict[str, str], start_param: str, start_value: str):
    return request(stream_name, {**base_params, start_param: start_value, "page": "1", "pageSize": str(PAGE_SIZE)})


@pytest.mark.parametrize("stream_name, primary_key, cursor_field, start_param, base_params", _INCREMENTAL_STREAMS)
def test_first_sync_starts_at_config_start_date_and_emits_latest_cursor(
    stream_name: str, primary_key: str, cursor_field: str, start_param: str, base_params: Dict[str, str]
) -> None:
    records = [
        {primary_key: 1, cursor_field: "2024-03-01T10:00:00.0000000"},
        {primary_key: 2, cursor_field: "2024-03-02T11:30:00.1230000"},
    ]
    with HttpMocker() as http_mocker:
        http_request = _page_one(stream_name, base_params, start_param, START_DATE_PARAM)
        http_mocker.get(http_request, json_response({stream_name: records, "page": 1, "pages": 1}))

        output = read_stream(stream_name, SyncMode.incremental)

        assert [record.record.data[primary_key] for record in output.records] == [1, 2]
        assert output.most_recent_state.stream_state.__dict__[cursor_field] == "2024-03-02T11:30:00.1230000"
        http_mocker.assert_number_of_calls(http_request, 1)


@pytest.mark.parametrize("stream_name, primary_key, cursor_field, start_param, base_params", _INCREMENTAL_STREAMS)
def test_second_sync_requests_from_state_minus_six_hour_lookback(
    stream_name: str, primary_key: str, cursor_field: str, start_param: str, base_params: Dict[str, str]
) -> None:
    state = StateBuilder().with_stream_state(stream_name, {cursor_field: "2024-03-02T11:30:00.1230000"}).build()
    records = [
        {primary_key: 2, cursor_field: "2024-03-02T11:30:00.1230000"},
        {primary_key: 3, cursor_field: "2024-03-05T09:15:00.0000000"},
    ]
    with HttpMocker() as http_mocker:
        http_request = _page_one(stream_name, base_params, start_param, "2024-03-02T05:30:00.1230000")
        http_mocker.get(http_request, json_response({stream_name: records, "page": 1, "pages": 1}))

        output = read_stream(stream_name, SyncMode.incremental, state=state)

        # The 6-hour lookback re-reads record 2, which sits exactly on the prior cursor.
        assert [record.record.data[primary_key] for record in output.records] == [2, 3]
        assert output.most_recent_state.stream_state.__dict__[cursor_field] == "2024-03-05T09:15:00.0000000"
        http_mocker.assert_number_of_calls(http_request, 1)
