#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType, StreamDescriptor, SyncMode, Type
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
from integration.response_builder import a_response_with_status


_EVENT_TYPES = ["customer.source.created", "customer.source.expiring", "customer.source.updated", "customer.source.deleted"]

_DATA_FIELD = NestedPath(["data", "object"])
_SOURCES_FIELD = FieldPath("sources")
_STREAM_NAME = "bank_accounts"
_CUSTOMERS_TEMPLATE_NAME = "customers_expand_data_source"
_BANK_ACCOUNTS_TEMPLATE_NAME = "bank_accounts"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
# FIXME expand[] is not documented anymore in stripe API doc (see https://github.com/airbytehq/airbyte/issues/33714)
_EXPANDS = ["data.sources"]
_OBJECT = "bank_account"
_A_CARD = RecordBuilder({"object": "card"}, None, None)
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)
_SLICE_STEP_SECONDS = 30 * 24 * 60 * 60


def _customers_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.customers_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _created_slice_bounds(start_date: datetime, end_date: datetime) -> list[tuple[int, int]]:
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    bounds = []
    while start_timestamp <= end_timestamp:
        slice_end = min(start_timestamp + _SLICE_STEP_SECONDS - 1, end_timestamp)
        bounds.append((start_timestamp, slice_end))
        start_timestamp = slice_end + 1
    return bounds


def _customers_slice_request(start_timestamp: int, end_timestamp: int, starting_after: Optional[str] = None) -> HttpRequest:
    request = (
        _customers_request()
        .with_expands(_EXPANDS)
        .with_created_gte(datetime.fromtimestamp(start_timestamp, tz=timezone.utc))
        .with_created_lte(datetime.fromtimestamp(end_timestamp, tz=timezone.utc))
        .with_limit(100)
    )
    if starting_after is not None:
        request.with_starting_after(starting_after)
    return request.build()


def _customers_bank_accounts_request(customer_id: str) -> StripeRequestBuilder:
    return StripeRequestBuilder.customers_bank_accounts_endpoint(customer_id, _ACCOUNT_ID, _CLIENT_SECRET)


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _config() -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(_NOW - timedelta(days=75))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_slice_range_in_days(365)
    )


def _config_with_start_date(start_date: datetime) -> ConfigBuilder:
    config = _config()
    config.build()["start_date"] = start_date.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return config


def _query_params(request: HttpRequest) -> Dict[str, list[str]]:
    return parse_qs(request._parsed_url.query)


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _an_event() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


def _a_customer() -> RecordBuilder:
    return create_record_builder(
        find_template(_CUSTOMERS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _customers_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_CUSTOMERS_TEMPLATE_NAME, __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy()
    )


def _a_bank_account() -> RecordBuilder:
    return create_record_builder(
        find_template(_BANK_ACCOUNTS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
    )


def _bank_accounts_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_BANK_ACCOUNTS_TEMPLATE_NAME, __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy()
    )


def _as_dict(response_builder: HttpResponseBuilder) -> Dict[str, Any]:
    return json.loads(response_builder.build().body)


def _read(
    config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[Dict[str, Any]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    return read(get_source(config, state), config, catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):
    @HttpMocker()
    def test_embedded_sources_emit_bank_accounts_and_filter_cards(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(
            _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]),
            _customers_response()
            .with_record(
                _a_customer().with_field(
                    _SOURCES_FIELD,
                    _as_dict(_bank_accounts_response().with_record(_a_bank_account()).with_record(_A_CARD)),
                )
            )
            .build(),
        )

        output = self._read(_config_with_start_date(start_date))

        assert len(output.records) == 1
        assert output.records[0].record.data["object"] == _OBJECT

    @HttpMocker()
    def test_sources_has_more_fetches_child_bank_accounts_page(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(
            _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]),
            _customers_response()
            .with_record(_a_customer().with_id("parent").with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_pagination())))
            .build(),
        )
        http_mocker.get(
            _customers_bank_accounts_request("parent").with_limit(100).build(),
            _bank_accounts_response().with_pagination().with_record(_a_bank_account().with_id("source_page_1")).build(),
        )
        http_mocker.get(
            _customers_bank_accounts_request("parent").with_limit(100).with_starting_after("source_page_1").build(),
            _bank_accounts_response().with_record(_a_bank_account().with_id("source_page_2")).build(),
        )

        output = self._read(_config_with_start_date(start_date))

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_multiple_customers_pages_when_read_then_query_pagination_on_parent(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        slice_bounds = _created_slice_bounds(start_date, _NOW)[0]
        http_mocker.get(
            _customers_slice_request(*slice_bounds),
            _customers_response()
            .with_pagination()
            .with_record(
                _a_customer()
                .with_id("customer_page_1")
                .with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account())))
            )
            .build(),
        )
        http_mocker.get(
            _customers_slice_request(*slice_bounds, starting_after="customer_page_1"),
            _customers_response()
            .with_record(_a_customer().with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account()))))
            .build(),
        )

        output = self._read(_config_with_start_date(start_date))

        assert len(output.records) == 2

    @HttpMocker()
    def test_empty_customer_slice_emits_no_records_or_errors(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(_customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]), _customers_response().build())

        output = self._read(_config_with_start_date(start_date))

        assert output.records == []
        assert output.errors == []

    @HttpMocker()
    def test_empty_sources_without_has_more_emits_no_records_or_errors(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(
            _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]),
            _customers_response().with_record(_a_customer().with_field(_SOURCES_FIELD, {"data": [], "has_more": False})).build(),
        )

        output = self._read(_config_with_start_date(start_date))

        assert output.records == []
        assert output.errors == []

    @HttpMocker()
    def test_mid_month_start_date_uses_integer_contiguous_slices(self, http_mocker: HttpMocker) -> None:
        start_date = (_NOW - timedelta(days=65)).replace(hour=12, minute=34, second=56, microsecond=0)
        slices = _created_slice_bounds(start_date, _NOW)
        for gte, lte in slices:
            request = _customers_slice_request(gte, lte)
            query_params = _query_params(request)
            assert query_params["created[gte]"] == [str(gte)]
            assert query_params["created[lte]"] == [str(lte)]
            http_mocker.get(request, _customers_response().build())

        output = self._read(_config_with_start_date(start_date))

        assert output.records == []
        assert len(slices) > 1
        assert all(next_gte == previous_lte + 1 for (_, previous_lte), (next_gte, _) in zip(slices, slices[1:]))
        assert slices[-1][1] == int(_NOW.timestamp())

    @HttpMocker()
    def test_missing_start_date_uses_default_epoch_range(self, http_mocker: HttpMocker) -> None:
        default_start_date = datetime(2017, 1, 25, tzinfo=timezone.utc)
        slices = _created_slice_bounds(default_start_date, _NOW)
        requests = []
        for gte, lte in slices:
            request = _customers_slice_request(gte, lte)
            http_mocker.get(request, _customers_response().build())
            requests.append(request)

        config = _config()
        config.build().pop("start_date")
        output = self._read(config)

        assert output.records == []
        first_request_params = _query_params(requests[0])
        assert first_request_params["created[gte]"] == ["1485302400"]
        assert first_request_params["created[lte]"] == [str(1485302400 + _SLICE_STEP_SECONDS - 1)]

    @HttpMocker()
    def test_full_refresh_emits_one_final_state(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(
            _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]),
            _customers_response()
            .with_record(_a_customer().with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account()))))
            .build(),
        )

        output = self._read(_config_with_start_date(start_date))

        assert len(output.state_messages) == 1
        assert output.records_and_state_messages[-1].type == Type.STATE
        state = vars(output.most_recent_state.stream_state)
        assert state == {
            "use_global_cursor": True,
            "state": {"updated": str(int(_NOW.timestamp()))},
            "lookback_window": 0,
        }

    @HttpMocker()
    def test_added_updated_field_is_an_integer(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(
            _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]),
            _customers_response()
            .with_record(
                _a_customer().with_field(
                    _SOURCES_FIELD,
                    _as_dict(_bank_accounts_response().with_record(_a_bank_account().with_field(FieldPath("created"), 1234567890))),
                )
            )
            .build(),
        )

        output = self._read(_config_with_start_date(start_date))

        updated = output.records[0].record.data["updated"]
        assert updated == 1234567890
        assert type(updated) is int

    @HttpMocker()
    def test_http_400_on_customers_fails_sync(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(
            _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]),
            a_response_with_status(400),
        )
        output = self._read(_config_with_start_date(start_date), expecting_exception=True)

        assert output.errors
        assert any(
            error.trace.error.failure_type == FailureType.system_error and "HTTP Status Code: 400" in error.trace.error.message
            for error in output.errors
        )
        assert output.records == []
        assert output.state_messages == []

    @HttpMocker()
    def test_given_http_status_401_when_read_then_config_error(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(
            _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]),
            a_response_with_status(401),
        )

        output = self._read(_config_with_start_date(start_date), expecting_exception=True)

        assert any(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
        assert output.records == []

    @HttpMocker()
    def test_given_http_status_500_when_read_then_raise_config_error(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        request = _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0])
        http_mocker.get(request, [a_response_with_status(500) for _ in range(6)])

        with patch("airbyte_cdk.sources.streams.http.rate_limiting.time.sleep"):
            output = self._read(_config_with_start_date(start_date), expecting_exception=True)

        http_mocker.assert_number_of_calls(request, 6)
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error
        assert output.records == []

    @HttpMocker()
    def test_http_403_and_404_on_customers_are_ignored(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=40)
        slices = _created_slice_bounds(start_date, _NOW)
        for (gte, lte), status_code in zip(slices, (403, 404)):
            response = (
                HttpResponse(json.dumps({"error": {"message": "Not found"}}), 404)
                if status_code == 404
                else a_response_with_status(status_code)
            )
            http_mocker.get(_customers_slice_request(gte, lte), response)

        output = self._read(_config_with_start_date(start_date))

        assert output.records == []
        assert output.errors == []

    @HttpMocker()
    def test_rate_limited_customers_request_retries_and_returns_records(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=10)
        http_mocker.get(
            _customers_slice_request(*_created_slice_bounds(start_date, _NOW)[0]),
            [
                a_response_with_status(429),
                _customers_response()
                .with_record(_a_customer().with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account()))))
                .build(),
            ],
        )
        with patch("airbyte_cdk.sources.streams.http.rate_limiting.time.sleep"):
            output = self._read(_config_with_start_date(start_date))
        assert len(output.records) == 1

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):
    @HttpMocker()
    def test_given_no_state_and_successful_sync_when_read_then_set_state_to_now(self, http_mocker: HttpMocker) -> None:
        # If stripe takes some time to ingest the data, we should recommend to use a lookback window when syncing the bank_accounts stream
        # to make sure that we don't lose data between the first and the second sync
        start_date = _NOW - timedelta(days=59)
        slices = _created_slice_bounds(start_date, _NOW)
        responses = []
        for index, (gte, lte) in enumerate(slices):
            response = _customers_response()
            if index == 0:
                response.with_record(
                    _a_customer().with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account())))
                )
            responses.append(response.build())
        http_mocker.get(_customers_request().with_any_query_params().build(), responses)

        output = self._read(_config_with_start_date(start_date), _NO_STATE)

        assert len(output.state_messages) == 1
        state = vars(output.most_recent_state.stream_state)
        assert state == {
            "use_global_cursor": True,
            "state": {"updated": str(int(_NOW.timestamp()))},
            "lookback_window": 0,
        }

    @HttpMocker()
    def test_given_state_when_read_then_query_events_using_types_and_state_value_plus_1(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=40)
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1

        http_mocker.get(
            _events_request().with_created_gte(state_datetime).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response()
            .with_record(_an_event().with_cursor(cursor_value).with_field(_DATA_FIELD, _a_bank_account().build()))
            .build(),
        )

        output = self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state.updated == str(cursor_value)

    @HttpMocker()
    def test_retention_state_older_than_30_days_is_cleared_for_full_customers_walk(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=60)
        config = _config_with_start_date(start_date)
        config.build()["api_retention_streams"] = [_STREAM_NAME]
        old_state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int((_NOW - timedelta(days=40)).timestamp())}).build()
        http_mocker.get(_customers_request().with_any_query_params().build(), _customers_response().build())

        output = self._read(config, old_state)

        assert output.records == []
        assert len(output.state_messages) == 2
        assert vars(output.state_messages[0].state.stream.stream_state) == {}
        final_state = vars(output.state_messages[-1].state.stream.stream_state)
        assert final_state["use_global_cursor"] is True
        assert final_state["lookback_window"] == 0

    @HttpMocker()
    def test_given_state_and_pagination_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        http_mocker.get(
            _events_request().with_created_gte(state_datetime).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response()
            .with_pagination()
            .with_record(_an_event().with_id("last_record_id_from_first_page").with_field(_DATA_FIELD, _a_bank_account().build()))
            .build(),
        )
        http_mocker.get(
            _events_request()
            .with_starting_after("last_record_id_from_first_page")
            .with_created_gte(state_datetime)
            .with_created_lte(_NOW)
            .with_limit(100)
            .with_types(_EVENT_TYPES)
            .build(),
            _events_response().with_record(self._a_bank_account_event()).build(),
        )

        output = self._read(
            _config(),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_state_and_small_slice_range_when_read_then_perform_multiple_queries(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        slice_range = timedelta(days=3)
        slice_datetime = state_datetime + slice_range

        http_mocker.get(
            _events_request()
            .with_created_gte(state_datetime)
            .with_created_lte(slice_datetime - _AVOIDING_INCLUSIVE_BOUNDARIES)
            .with_limit(100)
            .with_types(_EVENT_TYPES)
            .build(),
            _events_response().with_record(self._a_bank_account_event()).build(),
        )
        http_mocker.get(
            _events_request().with_created_gte(slice_datetime).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(self._a_bank_account_event()).with_record(self._a_bank_account_event()).build(),
        )

        output = self._read(
            _config().with_start_date(_NOW - timedelta(days=30)).with_slice_range_in_days(slice_range.days),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 3

    @HttpMocker()
    def test_given_state_earlier_than_30_days_when_read_then_query_events_using_types_and_event_lower_boundary(
        self, http_mocker: HttpMocker
    ) -> None:
        # this seems odd as we would miss some data between start_date and events_lower_boundary. In that case, we should hit the
        # customer endpoint
        start_date = _NOW - timedelta(days=40)
        state_value = _NOW - timedelta(days=39)
        events_lower_boundary = _NOW - timedelta(days=30)
        http_mocker.get(
            _events_request()
            .with_created_gte(events_lower_boundary)
            .with_created_lte(_NOW)
            .with_limit(100)
            .with_types(_EVENT_TYPES)
            .build(),
            _events_response().with_record(self._a_bank_account_event()).build(),
        )

        self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_value.timestamp())}).build(),
        )

        # request matched http_mocker

    @HttpMocker()
    def test_given_source_is_not_bank_account_when_read_then_filter_record(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        http_mocker.get(
            _events_request().with_created_gte(state_datetime).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(_an_event().with_field(_DATA_FIELD, _A_CARD.build())).build(),
        )

        output = self._read(
            _config(),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 0

    def _a_bank_account_event(self) -> RecordBuilder:
        return _an_event().with_field(_DATA_FIELD, _a_bank_account().build())

    def _read(self, config: ConfigBuilder, state: Optional[Dict[str, Any]], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)
