# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.sources.source import TState
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
from airbyte_protocol.models import AirbyteStateBlob, AirbyteStreamState, ConfiguredAirbyteCatalog, FailureType, StreamDescriptor, SyncMode
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder
from integration.response_builder import a_response_with_status
from source_stripe import SourceStripe

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
_NOT_A_BANK_ACCOUNT = RecordBuilder({"object": "NOT a bank account"}, None, None)
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)


def _customers_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.customers_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _customers_bank_accounts_request(customer_id: str) -> StripeRequestBuilder:
    return StripeRequestBuilder.customers_bank_accounts_endpoint(customer_id, _ACCOUNT_ID, _CLIENT_SECRET)


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _config() -> ConfigBuilder:
    return ConfigBuilder().with_start_date(_NOW - timedelta(days=75)).with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> SourceStripe:
    return SourceStripe(catalog, config, state)


def _an_event() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template("events", __file__),
        FieldPath("data"),
        pagination_strategy=StripePaginationStrategy()
    )


def _a_customer() -> RecordBuilder:
    return create_record_builder(
        find_template(_CUSTOMERS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _customers_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_CUSTOMERS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        pagination_strategy=StripePaginationStrategy()
    )


def _a_bank_account() -> RecordBuilder:
    return create_record_builder(
        find_template(_BANK_ACCOUNTS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
    )


def _bank_accounts_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_BANK_ACCOUNTS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        pagination_strategy=StripePaginationStrategy()
    )


def _given_customers_availability_check(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        StripeRequestBuilder.customers_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_any_query_params().build(),
        _customers_response().with_record(_a_customer()).build()  # there needs to be a record in the parent stream for the child to be available
    )


def _given_events_availability_check(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_any_query_params().build(),
        _events_response().build()
    )


def _as_dict(response_builder: HttpResponseBuilder) -> Dict[str, Any]:
    return json.loads(response_builder.build().body)


def _read(
    config_builder: ConfigBuilder,
    sync_mode: SyncMode,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    return read(_source(catalog, config, state), config, catalog, state, expecting_exception)


def _assert_not_available(output: EntrypointOutput) -> None:
    # right now, no stream statuses means stream unavailable
    assert len(output.get_stream_statuses(_STREAM_NAME)) == 0


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):
    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response()
            .with_record(
                _a_customer()
                .with_field(
                    _SOURCES_FIELD,
                    _as_dict(
                        _bank_accounts_response()
                        .with_record(_a_bank_account())
                        .with_record(_a_bank_account())
                    )
                )
            )
            .with_record(
                _a_customer()
                .with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account())))
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 3

    @HttpMocker()
    def test_given_source_is_not_bank_account_when_read_then_filter_record(self, http_mocker: HttpMocker) -> None:
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response()
            .with_record(
                _a_customer()
                .with_field(
                    _SOURCES_FIELD,
                    _as_dict(
                        _bank_accounts_response()
                        .with_record(_NOT_A_BANK_ACCOUNT)
                    )
                )
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 0

    @HttpMocker()
    def test_given_multiple_bank_accounts_pages_when_read_then_query_pagination_on_child(self, http_mocker: HttpMocker) -> None:
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response()
            .with_record(
                _a_customer()
                .with_id("parent_id")
                .with_field(
                    _SOURCES_FIELD,
                    _as_dict(
                        _bank_accounts_response()
                        .with_pagination()
                        .with_record(_a_bank_account().with_id("latest_bank_account_id"))
                    )
                )
            ).build(),
        )
        http_mocker.get(
            # we do not use slice boundaries here because:
            # * there should be no duplicates parents (application fees) returned by the stripe API as it is using cursor pagination
            # * it is implicitly lower bounder by the parent creation
            # * the upper boundary is not configurable and is always <now>
            _customers_bank_accounts_request("parent_id").with_limit(100).with_starting_after("latest_bank_account_id").build(),
            _bank_accounts_response().with_record(_a_bank_account()).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_multiple_customers_pages_when_read_then_query_pagination_on_parent(self, http_mocker: HttpMocker) -> None:
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response()
            .with_pagination()
            .with_record(
                _a_customer()
                .with_id("parent_id")
                .with_field(
                    _SOURCES_FIELD,
                    _as_dict(
                        _bank_accounts_response()
                        .with_record(_a_bank_account())
                    )
                )
            ).build(),
        )
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_starting_after("parent_id").with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response()
            .with_record(
                _a_customer()
                .with_field(
                    _SOURCES_FIELD,
                    _as_dict(
                        _bank_accounts_response()
                        .with_record(_a_bank_account())
                    )
                )
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_parent_stream_without_bank_accounts_when_read_then_stream_is_unavailable(self, http_mocker: HttpMocker) -> None:
        # events stream is not validated as application fees is validated first
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response().build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        _assert_not_available(output)

    @HttpMocker()
    def test_given_slice_range_when_read_then_perform_multiple_requests(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range

        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(start_date).with_created_lte(slice_datetime).with_limit(100).build(),
            _customers_response().with_record(
                _a_customer()
                .with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account())))
            ).build(),
        )
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(slice_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response().with_record(
                _a_customer()
                .with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account())))
            ).build(),
        )

        output = self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_slice_range_and_bank_accounts_pagination_when_read_then_do_not_slice_child(self, http_mocker: HttpMocker) -> None:
        """
        This means that if the user attempt to configure the slice range, it will only apply on the parent stream
        """
        start_date = _NOW - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range

        _given_events_availability_check(http_mocker)
        http_mocker.get(
            StripeRequestBuilder.customers_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_any_query_params().build(),
            _customers_response().build()
        )  # catching subsequent slicing request that we don't really care for this test
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(start_date).with_created_lte(slice_datetime).with_limit(100).build(),
            _customers_response().with_record(
                _a_customer()
                .with_id("parent_id")
                .with_field(
                    _SOURCES_FIELD,
                    _as_dict(
                        _bank_accounts_response()
                        .with_pagination()
                        .with_record(_a_bank_account().with_id("latest_bank_account_id"))
                    )
                )
            ).build(),
        )
        http_mocker.get(
            # slice range is not applied here
            _customers_bank_accounts_request("parent_id").with_limit(100).with_starting_after("latest_bank_account_id").build(),
            _bank_accounts_response().with_record(_a_bank_account()).build(),
        )

        self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))

        # request matched http_mocker

    @HttpMocker()
    def test_given_no_state_when_read_then_return_ignore_lookback(self, http_mocker: HttpMocker) -> None:
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response().with_record(_a_customer()).build(),
        )

        self._read(_config().with_start_date(_A_START_DATE).with_lookback_window_in_days(10))

        # request matched http_mocker

    @HttpMocker()
    def test_given_one_page_when_read_then_cursor_field_is_set(self, http_mocker: HttpMocker) -> None:
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response()
            .with_record(
                _a_customer()
                .with_field(
                    _SOURCES_FIELD,
                    _as_dict(
                        _bank_accounts_response()
                        .with_record(_a_bank_account())
                    )
                )
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert output.records[0].record.data["updated"] == int(_NOW.timestamp())

    @HttpMocker()
    def test_given_http_status_401_when_read_then_system_error(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _customers_request().with_any_query_params().build(),
            a_response_with_status(401),
        )
        output = self._read(_config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.system_error

    @HttpMocker()
    def test_given_rate_limited_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_any_query_params().build(),
            [
                a_response_with_status(429),
                _customers_response().with_record(_a_customer().with_field(
                    _SOURCES_FIELD,
                    _as_dict(
                        _bank_accounts_response()
                        .with_record(_a_bank_account())
                    )
                )).build(),
            ],
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_on_availability_when_read_then_raise_system_error(self, http_mocker: HttpMocker) -> None:
        request = _customers_request().with_any_query_params().build()
        http_mocker.get(
            request,
            a_response_with_status(500),
        )
        output = self._read(_config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.system_error

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):

    @HttpMocker()
    def test_given_no_state_and_successful_sync_when_read_then_set_state_to_now(self, http_mocker: HttpMocker) -> None:
        # If stripe takes some time to ingest the data, we should recommend to use a lookback window when syncing the bank_accounts stream
        # to make sure that we don't lose data between the first and the second sync
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _customers_request().with_expands(_EXPANDS).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _customers_response().with_record(
                _a_customer()
                .with_field(_SOURCES_FIELD, _as_dict(_bank_accounts_response().with_record(_a_bank_account())))
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE), _NO_STATE)

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(updated=int(_NOW.timestamp()))

    @HttpMocker()
    def test_given_state_when_read_then_query_events_using_types_and_state_value_plus_1(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=40)
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1

        _given_customers_availability_check(http_mocker)
        _given_events_availability_check(http_mocker)
        http_mocker.get(
            _events_request().with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(
                _an_event().with_cursor(cursor_value).with_field(_DATA_FIELD, _a_bank_account().build())
            ).build(),
        )

        output = self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(updated=cursor_value)

    @HttpMocker()
    def test_given_state_and_pagination_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        _given_customers_availability_check(http_mocker)
        _given_events_availability_check(http_mocker)
        state_datetime = _NOW - timedelta(days=5)
        http_mocker.get(
            _events_request().with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_pagination().with_record(
                _an_event().with_id("last_record_id_from_first_page").with_field(_DATA_FIELD, _a_bank_account().build())
            ).build(),
        )
        http_mocker.get(
            _events_request().with_starting_after("last_record_id_from_first_page").with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
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
        slice_datetime = state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES + slice_range

        _given_customers_availability_check(http_mocker)
        _given_events_availability_check(http_mocker)  # the availability check does not consider the state so we need to define a generic availability check
        http_mocker.get(
            _events_request().with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(slice_datetime).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(self._a_bank_account_event()).build(),
        )
        http_mocker.get(
            _events_request().with_created_gte(slice_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(self._a_bank_account_event()).with_record(self._a_bank_account_event()).build(),
        )

        output = self._read(
            _config().with_start_date(_NOW - timedelta(days=30)).with_slice_range_in_days(slice_range.days),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 3

    @HttpMocker()
    def test_given_state_earlier_than_30_days_when_read_then_query_events_using_types_and_event_lower_boundary(self, http_mocker: HttpMocker) -> None:
        # this seems odd as we would miss some data between start_date and events_lower_boundary. In that case, we should hit the
        # customer endpoint
        _given_customers_availability_check(http_mocker)
        start_date = _NOW - timedelta(days=40)
        state_value = _NOW - timedelta(days=39)
        events_lower_boundary = _NOW - timedelta(days=30)
        http_mocker.get(
            _events_request().with_created_gte(events_lower_boundary).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(self._a_bank_account_event()).build(),
        )

        self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_value.timestamp())}).build(),
        )

        # request matched http_mocker

    @HttpMocker()
    def test_given_source_is_not_bank_account_when_read_then_filter_record(self, http_mocker: HttpMocker) -> None:
        _given_customers_availability_check(http_mocker)
        _given_events_availability_check(http_mocker)
        state_datetime = _NOW - timedelta(days=5)
        http_mocker.get(
            _events_request().with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(
                _an_event().with_field(_DATA_FIELD, _NOT_A_BANK_ACCOUNT.build())
            ).build(),
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
