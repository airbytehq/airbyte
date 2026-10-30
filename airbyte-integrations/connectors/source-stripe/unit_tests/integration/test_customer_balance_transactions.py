#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
from unittest import TestCase

import freezegun
import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder


_STREAM_NAME = "customer_balance_transactions"
_CUSTOMER_STREAM = "customers"
_EVENT_STREAM = "cbt_customer_events"
_NOW = datetime.now(timezone.utc)
_START_DATE = _NOW - timedelta(days=20)
_ACCOUNT_ID = ConfigBuilder().build()["account_id"]
_CLIENT_SECRET = ConfigBuilder().build()["client_secret"]
_EVENT_OBJECT = NestedPath(["data", "object"])
_WINDOW_DAYS = 7


def _config(start_date: datetime = _START_DATE) -> ConfigBuilder:
    return ConfigBuilder().with_start_date(start_date).with_slice_range_in_days(365)


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()


def _read(
    config_builder: ConfigBuilder,
    state: Optional[List[Any]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    config = config_builder.build()
    return read(
        get_source(config, state),
        config,
        _catalog(),
        state,
        expecting_exception,
    )


def _stream_state(output: EntrypointOutput) -> Dict[str, Any]:
    return vars(output.state_messages[-1].state.stream.stream_state)


def _resume_state(output: EntrypointOutput, input_state: Optional[List[Any]]) -> Optional[List[Any]]:
    return [output.state_messages[-1].state] if output.state_messages else input_state


def _state(stream_state: Dict[str, Any]) -> List[Any]:
    return StateBuilder().with_stream_state(_STREAM_NAME, stream_state).build()


def _customer_request(start: datetime, end: datetime) -> HttpRequest:
    return (
        StripeRequestBuilder.customers_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)
        .with_created_gte(start)
        .with_created_lte(end)
        .with_limit(100)
        .build()
    )


@lru_cache(maxsize=None)
def _child_request(customer_id: str) -> HttpRequest:
    return (
        StripeRequestBuilder._for_endpoint(f"customers/{customer_id}/balance_transactions", _ACCOUNT_ID, _CLIENT_SECRET)
        .with_any_query_params()
        .build()
    )


def _events_request() -> HttpRequest:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_any_query_params().build()


def _created_windows(start: datetime, end: datetime) -> List[Tuple[datetime, datetime]]:
    windows = []
    window_start = start
    while window_start <= end:
        window_end = min(window_start + timedelta(days=_WINDOW_DAYS) - timedelta(seconds=1), end)
        windows.append((window_start, window_end))
        window_start = window_end + timedelta(seconds=1)
    return windows


def _customer_record(customer_id: str, created: datetime) -> RecordBuilder:
    return (
        create_record_builder(
            find_template("customer_balance_transactions_customers", __file__),
            FieldPath("data"),
            record_id_path=FieldPath("id"),
            record_cursor_path=FieldPath("created"),
        )
        .with_id(customer_id)
        .with_field(FieldPath("created"), int(created.timestamp()))
    )


def _customers_response(customers: List[Tuple[str, datetime]]) -> HttpResponseBuilder:
    response = create_response_builder(
        find_template("customer_balance_transactions_customers", __file__),
        FieldPath("data"),
        pagination_strategy=StripePaginationStrategy(),
    )
    for customer_id, created in sorted(customers, key=lambda item: item[1], reverse=True):
        response.with_record(_customer_record(customer_id, created))
    return response


def _transaction_record() -> RecordBuilder:
    return create_record_builder(
        find_template("customer_balance_transactions", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _transactions_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template("customer_balance_transactions", __file__),
        FieldPath("data"),
        pagination_strategy=StripePaginationStrategy(),
    ).with_record(_transaction_record())


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template("customer_balance_transactions_events", __file__),
        FieldPath("data"),
        pagination_strategy=StripePaginationStrategy(),
    )


def _event_record(customer_id: str, customer_created: datetime, event_created: datetime) -> RecordBuilder:
    return (
        create_record_builder(
            find_template("customer_balance_transactions_events", __file__),
            FieldPath("data"),
            record_id_path=FieldPath("id"),
            record_cursor_path=FieldPath("created"),
        )
        .with_id("synthetic-event")
        .with_field(FieldPath("type"), "customer.updated")
        .with_field(FieldPath("created"), int(event_created.timestamp()))
        .with_field(
            _EVENT_OBJECT,
            _customer_record(customer_id, customer_created).build(),
        )
    )


def _register_events(http_mocker: HttpMocker, response: Optional[HttpResponseBuilder] = None) -> None:
    http_mocker.get(_events_request(), (response or _events_response()).build())


def _status_response(status_code: int) -> HttpResponse:
    return HttpResponse(
        json.dumps({"error": {"type": "invalid_request_error", "message": "Synthetic request failure"}}),
        status_code,
    )


def _register_customer_windows(
    http_mocker: HttpMocker,
    start: datetime,
    customers_by_window: Dict[int, List[Tuple[str, datetime]]],
    end: datetime = _NOW,
) -> None:
    for index, (window_start, window_end) in enumerate(_created_windows(start, end)):
        http_mocker.get(
            _customer_request(window_start, window_end),
            _customers_response(customers_by_window.get(index, [])).build(),
        )


def _register_children(http_mocker: HttpMocker, customer_ids: List[str]) -> None:
    for customer_id in customer_ids:
        http_mocker.get(_child_request(customer_id), _transactions_response().build())


def _placeholder_state(customers_updated: datetime) -> Dict[str, Any]:
    return {
        "use_global_cursor": True,
        "lookback_window": 0,
        "parent_state": {_CUSTOMER_STREAM: {"updated": int(customers_updated.timestamp())}},
    }


def _walk_state(customers_updated: datetime, events_updated: datetime) -> Dict[str, Any]:
    return {
        "use_global_cursor": True,
        "lookback_window": 0,
        "state": {"created": int(customers_updated.timestamp())},
        "parent_state": {
            _CUSTOMER_STREAM: {"updated": int(customers_updated.timestamp())},
            _EVENT_STREAM: {"updated": int(events_updated.timestamp())},
        },
    }


@freezegun.freeze_time(_NOW.isoformat())
class CustomerBalanceTransactionsTest(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_walk_all_customers_and_emit_both_parent_states(self, http_mocker: HttpMocker) -> None:
        windows = _created_windows(_START_DATE, _NOW)
        customers = [
            ("synthetic-1", windows[0][0] + timedelta(hours=1)),
            ("synthetic-2", windows[1][0] + timedelta(hours=1)),
            ("synthetic-3", windows[2][0] + timedelta(hours=1)),
        ]
        _register_customer_windows(http_mocker, _START_DATE, {i: [record] for i, record in enumerate(customers)})
        _register_events(http_mocker)
        _register_children(http_mocker, [customer_id for customer_id, _ in customers])

        output = _read(_config())

        assert not output.errors
        assert len(output.records) == len(customers)
        state = _stream_state(output)
        assert {"customers", "cbt_customer_events"}.issubset(state["parent_state"])
        for customer_id, _ in customers:
            http_mocker.assert_number_of_calls(_child_request(customer_id), 1)

    @HttpMocker()
    def test_given_placeholder_state_when_read_then_walk_from_start_date(self, http_mocker: HttpMocker) -> None:
        windows = _created_windows(_START_DATE, _NOW)
        customers = [(f"synthetic-{index + 1}", window[0] + timedelta(hours=1)) for index, window in enumerate(windows)]
        initial_state = _state(_placeholder_state(_START_DATE))
        _register_customer_windows(http_mocker, _START_DATE, {i: [record] for i, record in enumerate(customers)})
        _register_events(http_mocker)
        _register_children(http_mocker, [customer_id for customer_id, _ in customers])

        output = _read(_config(), initial_state)

        assert not output.errors
        for customer_id, _ in customers:
            http_mocker.assert_number_of_calls(_child_request(customer_id), 1)

    @HttpMocker()
    def test_given_completed_hdp_state_when_read_then_walk_from_mark_and_read_events(self, http_mocker: HttpMocker) -> None:
        mark = _START_DATE + timedelta(days=10)
        windows = _created_windows(mark, _NOW)
        eligible = [("synthetic-2", windows[0][0] + timedelta(hours=1)), ("synthetic-3", windows[-1][0] + timedelta(hours=1))]
        initial_state = _state(_walk_state(mark, _NOW - timedelta(days=1)))
        _register_customer_windows(http_mocker, mark, {0: [eligible[0]], len(windows) - 1: [eligible[1]]})
        _register_events(http_mocker)
        _register_children(http_mocker, [customer_id for customer_id, _ in eligible])

        output = _read(_config(), initial_state)

        assert not output.errors
        assert len(output.records) == len(eligible)
        for customer_id, _ in eligible:
            http_mocker.assert_number_of_calls(_child_request(customer_id), 1)

    @HttpMocker()
    def test_given_703_post_events_state_when_read_then_add_events_parent_state(self, http_mocker: HttpMocker) -> None:
        mark = _START_DATE + timedelta(days=7)
        windows = _created_windows(mark, _NOW)
        customers = [("synthetic-2", windows[0][0] + timedelta(hours=1))]
        initial_state = _state(_placeholder_state(mark))
        _register_customer_windows(http_mocker, mark, {0: customers})
        _register_events(http_mocker)
        _register_children(http_mocker, ["synthetic-2"])

        output = _read(_config(), initial_state)

        assert not output.errors
        assert "cbt_customer_events" in _stream_state(output)["parent_state"]

    @HttpMocker()
    def test_given_mid_walk_state_when_read_then_resume_from_customer_cursor(self, http_mocker: HttpMocker) -> None:
        mark = _START_DATE + timedelta(days=9)
        windows = _created_windows(mark, _NOW)
        boundary_customer = ("synthetic-boundary", mark)
        later_customer = ("synthetic-later", windows[0][0] + timedelta(days=2))
        initial_state = _state(_walk_state(mark, _START_DATE + timedelta(days=8)))
        _register_customer_windows(http_mocker, mark, {0: [boundary_customer, later_customer]})
        _register_events(http_mocker)
        _register_children(http_mocker, ["synthetic-boundary", "synthetic-later"])

        output = _read(_config(), initial_state)

        assert not output.errors
        http_mocker.assert_number_of_calls(_child_request("synthetic-boundary"), 1)
        http_mocker.assert_number_of_calls(_child_request("synthetic-later"), 1)

    def _assert_failed_walk_does_not_read_oldest_customer(self, status_code: int) -> None:
        windows = _created_windows(_START_DATE, _NOW)
        newest = ("synthetic-newest", windows[0][0] + timedelta(days=5))
        oldest = ("synthetic-oldest", windows[0][0] + timedelta(days=1))
        input_state = _state(_placeholder_state(_START_DATE))

        with HttpMocker() as http_mocker:
            http_mocker.get(_customer_request(*windows[0]), _customers_response([newest, oldest]).build())
            http_mocker.get(_customer_request(*windows[1]), _status_response(status_code))
            _register_events(http_mocker)
            _register_children(http_mocker, ["synthetic-newest", "synthetic-oldest"])

            attempt_a = _read(_config(), input_state, expecting_exception=True)

            assert attempt_a.errors
            http_mocker.assert_number_of_calls(_child_request("synthetic-oldest"), 0)

    def _assert_failed_walk_resumes_oldest_customer(self, status_code: int) -> None:
        windows = _created_windows(_START_DATE, _NOW)
        newest = ("synthetic-newest", windows[0][0] + timedelta(days=5))
        oldest = ("synthetic-oldest", windows[0][0] + timedelta(days=1))
        input_state = _state(_placeholder_state(_START_DATE))
        error_state: Optional[List[Any]] = None

        with HttpMocker() as http_mocker:
            http_mocker.get(_customer_request(*windows[0]), _customers_response([newest, oldest]).build())
            http_mocker.get(_customer_request(*windows[1]), _status_response(status_code))
            _register_events(http_mocker)
            _register_children(http_mocker, ["synthetic-newest"])
            attempt_a = _read(_config(), input_state, expecting_exception=True)
            assert attempt_a.errors
            state_a = _stream_state(attempt_a)
            assert int(state_a["parent_state"]["customers"]["updated"]) < int(oldest[1].timestamp())
            error_state = _resume_state(attempt_a, input_state)

        with HttpMocker() as http_mocker:
            _register_customer_windows(http_mocker, _START_DATE, {0: [newest, oldest]})
            _register_events(http_mocker)
            _register_children(http_mocker, ["synthetic-newest", "synthetic-oldest"])
            attempt_b = _read(_config(), error_state)
            assert not attempt_b.errors
            http_mocker.assert_number_of_calls(_child_request("synthetic-oldest"), 1)

    def test_given_second_customer_window_returns_400_when_read_then_sync_fails(self) -> None:
        self._assert_failed_walk_does_not_read_oldest_customer(400)

    @pytest.mark.xfail(
        strict=True,
        reason="requires airbyte-cdk with airbytehq/airbyte-python-cdk#1257",
    )
    def test_given_second_customer_window_returns_400_when_resume_then_oldest_customer_is_read(self) -> None:
        self._assert_failed_walk_resumes_oldest_customer(400)

    def test_given_second_customer_window_returns_403_when_read_then_sync_fails(self) -> None:
        self._assert_failed_walk_does_not_read_oldest_customer(403)

    @pytest.mark.xfail(
        strict=True,
        reason="requires airbyte-cdk with airbytehq/airbyte-python-cdk#1257",
    )
    def test_given_second_customer_window_returns_403_when_resume_then_oldest_customer_is_read(self) -> None:
        self._assert_failed_walk_resumes_oldest_customer(403)

    @HttpMocker()
    def test_given_events_parent_returns_400_when_read_then_sync_fails(self, http_mocker: HttpMocker) -> None:
        state = _state(
            {
                "use_global_cursor": True,
                "lookback_window": 0,
                "state": {"created": int(_NOW.timestamp())},
                "parent_state": {
                    "customers": {"updated": int((_NOW + timedelta(days=1)).timestamp())},
                    "cbt_customer_events": {"updated": int((_NOW - timedelta(days=1)).timestamp())},
                },
            }
        )
        http_mocker.get(_events_request(), _status_response(400))

        output = _read(_config(), state, expecting_exception=True)

        assert output.errors

    @HttpMocker()
    def test_given_events_parent_returns_403_when_read_then_sync_fails(self, http_mocker: HttpMocker) -> None:
        state = _state(
            {
                "use_global_cursor": True,
                "lookback_window": 0,
                "state": {"created": int(_NOW.timestamp())},
                "parent_state": {
                    "customers": {"updated": int((_NOW + timedelta(days=1)).timestamp())},
                    "cbt_customer_events": {"updated": int((_NOW - timedelta(days=1)).timestamp())},
                },
            }
        )
        http_mocker.get(_events_request(), _status_response(403))

        output = _read(_config(), state, expecting_exception=True)

        assert output.errors

    @HttpMocker()
    def test_given_child_returns_404_when_read_then_other_customers_are_emitted(self, http_mocker: HttpMocker) -> None:
        window = _created_windows(_START_DATE, _NOW)[0]
        customers = [("synthetic-missing", window[0] + timedelta(hours=1)), ("synthetic-present", window[0] + timedelta(hours=2))]
        _register_customer_windows(http_mocker, _START_DATE, {0: customers})
        _register_events(http_mocker)
        http_mocker.get(_child_request("synthetic-missing"), _status_response(404))
        http_mocker.get(_child_request("synthetic-present"), _transactions_response().build())

        output = _read(_config())

        assert not output.errors
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_child_returns_403_when_read_then_sync_fails(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=1)
        window = _created_windows(start_date, _NOW)[0]
        customer = ("synthetic-customer", window[0] + timedelta(hours=1))
        initial_state = _state(
            {
                "use_global_cursor": True,
                "lookback_window": 0,
                "state": {"created": int(start_date.timestamp())},
                "parent_state": {
                    "customers": {"updated": int(start_date.timestamp())},
                    "cbt_customer_events": {"updated": int((_NOW + timedelta(days=1)).timestamp())},
                },
            }
        )
        _register_customer_windows(http_mocker, start_date, {0: [customer]})
        http_mocker.get(_child_request(customer[0]), _status_response(403))

        output = _read(_config(start_date), initial_state, expecting_exception=True)

        assert output.errors

    @HttpMocker()
    def test_given_completed_state_and_old_customer_updated_event_when_read_then_request_customer_child(
        self, http_mocker: HttpMocker
    ) -> None:
        mark = _NOW - timedelta(days=1)
        old_customer_created = _START_DATE - timedelta(days=100)
        initial_state = _state(_walk_state(mark, mark))
        _register_customer_windows(http_mocker, mark, {})
        _register_events(
            http_mocker,
            _events_response().with_record(_event_record("synthetic-old", old_customer_created, _NOW - timedelta(hours=1))),
        )
        _register_children(http_mocker, ["synthetic-old"])

        output = _read(_config(), initial_state)

        assert not output.errors
        http_mocker.assert_number_of_calls(_child_request("synthetic-old"), 1)
