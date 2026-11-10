# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Optional

import freezegun
import pytest

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder
from airbyte_cdk.test.state_builder import StateBuilder

from ..config import ACCESS_TOKEN, ConfigBuilder
from ..request_builder import RequestBuilder
from ..response_builder import NEXT_PAGE_TOKEN, get_stream_record, get_stream_response
from ..utils import get_cursor_value_from_state_message, read_full_refresh, read_incremental


def orders_config(deprecated: Optional[bool], start: str = "2024-01-01T00:00:00Z") -> ConfigBuilder:
    config = ConfigBuilder().with_start_date(start)
    if deprecated is not None:
        config.build()["use_orders_deprecated_api"] = deprecated
    return config


def orders_request(version: str) -> RequestBuilder:
    return RequestBuilder.get_endpoint("orders").with_access_token(ACCESS_TOKEN).with_old_api_version(version).with_limit(250)


def orders_response(ids: range, updated_at: str = "2024-01-01 00:00:00") -> HttpResponseBuilder:
    response = get_stream_response("orders")
    for record_id in ids:
        response.with_record(get_stream_record("orders", "id", "updated_at").with_id(record_id).with_cursor(updated_at))
    return response


@pytest.mark.parametrize("deprecated,version", [(True, "2021-01"), (False, "2021-11"), (None, "2021-11")])
@freezegun.freeze_time("2024-01-30T23:59:59Z")
def test_api_version_switch(deprecated: Optional[bool], version: str) -> None:
    request = orders_request(version).with_updated_at_range("2024-01-01 00:00:00", "2024-01-30 23:59:59").build()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, orders_response(range(101, 102)).build())
        output = read_full_refresh(orders_config(deprecated), "orders")
        assert [record.record.data["id"] for record in output.records] == [101]
        http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time("2024-02-29T23:59:59Z")
def test_deprecated_pages_restart_in_each_thirty_day_slice() -> None:
    first = orders_request("2021-01").with_updated_at_range("2024-01-01 00:00:00", "2024-01-30 23:59:59").build()
    second = orders_request("2021-01").with_updated_at_range("2024-01-01 00:00:00", "2024-01-30 23:59:59").with_page(2).build()
    next_slice = orders_request("2021-01").with_updated_at_range("2024-01-31 00:00:00", "2024-02-29 23:59:59").build()
    next_slice_second = orders_request("2021-01").with_updated_at_range("2024-01-31 00:00:00", "2024-02-29 23:59:59").with_page(2).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(first, orders_response(range(1, 251)).build())
        http_mocker.get(second, orders_response(range(251, 252)).build())
        http_mocker.get(next_slice, orders_response(range(252, 502), "2024-02-01 00:00:00").build())
        http_mocker.get(next_slice_second, orders_response(range(502, 503), "2024-02-01 00:00:00").build())
        output = read_incremental(orders_config(True), "orders")
        assert sorted(record.record.data["id"] for record in output.records) == list(range(1, 503))
        assert get_cursor_value_from_state_message(output, "updated_at") == "2024-02-01 00:00:00"
        for request in (first, second, next_slice, next_slice_second):
            http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time("2024-01-30T23:59:59Z")
def test_modern_cursor_page_sends_only_cursor_and_limit() -> None:
    first = orders_request("2021-11").with_updated_at_range("2024-01-01 00:00:00", "2024-01-30 23:59:59").build()
    second = orders_request("2021-11").with_next_page_token(NEXT_PAGE_TOKEN).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(first, orders_response(range(101, 102)).with_pagination().build())
        http_mocker.get(second, orders_response(range(102, 103)).build())
        output = read_full_refresh(orders_config(False), "orders")
        assert [record.record.data["id"] for record in output.records] == [101, 102]
        for request in (first, second):
            http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("deprecated,version", [(True, "2021-01"), (False, "2021-11")])
@pytest.mark.parametrize("cursor", ["2024-01-01 00:00:00", "2024-01-01T00:00:00+00:00"])
@freezegun.freeze_time("2024-01-30T23:59:59Z")
def test_legacy_state_replays_inclusive_boundary(deprecated: bool, version: str, cursor: str) -> None:
    state = StateBuilder().with_stream_state("orders", {"updated_at": cursor}).build()
    request = orders_request(version).with_updated_at_range("2024-01-01 00:00:00", "2024-01-30 23:59:59").build()
    with HttpMocker() as http_mocker:
        response = orders_response(range(101, 102))
        response.with_record(get_stream_record("orders", "id", "updated_at").with_id(102).with_cursor("2024-01-02 00:00:00"))
        http_mocker.get(request, response.build())
        output = read_incremental(orders_config(deprecated, "2020-01-01T00:00:00Z"), "orders", state)
        assert [record.record.data["id"] for record in output.records] == [101, 102]
        assert get_cursor_value_from_state_message(output, "updated_at") == "2024-01-02 00:00:00"
        http_mocker.assert_number_of_calls(request, 1)
