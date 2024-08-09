# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase
from unittest.mock import patch

import freezegun
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams.http.error_handlers.http_status_error_handler import HttpStatusErrorHandler
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
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
from airbyte_protocol.models import AirbyteStateBlob, ConfiguredAirbyteCatalog, FailureType, StreamDescriptor, SyncMode
from integration.config import ConfigBuilder
from integration.helpers import assert_stream_did_not_run
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder
from integration.response_builder import a_response_with_status
from source_stripe import SourceStripe

_EVENT_TYPES = ["application_fee.refund.updated"]

_DATA_FIELD = NestedPath(["data", "object"])
_REFUNDS_FIELD = FieldPath("refunds")
_STREAM_NAME = "application_fees_refunds"
_APPLICATION_FEES_TEMPLATE_NAME = "application_fees"
_REFUNDS_TEMPLATE_NAME = "application_fees_refunds"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)


def _application_fees_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.application_fees_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _application_fees_refunds_request(application_fee_id: str) -> StripeRequestBuilder:
    return StripeRequestBuilder.application_fees_refunds_endpoint(application_fee_id, _ACCOUNT_ID, _CLIENT_SECRET)


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


def _an_application_fee() -> RecordBuilder:
    return create_record_builder(
        find_template(_APPLICATION_FEES_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _application_fees_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_APPLICATION_FEES_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        pagination_strategy=StripePaginationStrategy()
    )


def _a_refund() -> RecordBuilder:
    return create_record_builder(
        find_template(_REFUNDS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _refunds_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_REFUNDS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        pagination_strategy=StripePaginationStrategy()
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


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):
    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _application_fees_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response()
            .with_record(
                _an_application_fee()
                .with_field(
                    _REFUNDS_FIELD,
                    _as_dict(
                        _refunds_response()
                        .with_record(_a_refund())
                        .with_record(_a_refund())
                    )
                )
            )
            .with_record(
                _an_application_fee()
                .with_field(_REFUNDS_FIELD, _as_dict(_refunds_response().with_record(_a_refund())))
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 3

    @HttpMocker()
    def test_given_multiple_refunds_pages_when_read_then_query_pagination_on_child(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _application_fees_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response()
            .with_record(
                _an_application_fee()
                .with_id("parent_id")
                .with_field(
                    _REFUNDS_FIELD,
                    _as_dict(
                        _refunds_response()
                        .with_pagination()
                        .with_record(_a_refund().with_id("latest_refund_id"))
                    )
                )
            ).build(),
        )
        http_mocker.get(
            # we do not use slice boundaries here because:
            # * there should be no duplicates parents (application fees) returned by the stripe API as it is using cursor pagination
            # * it is implicitly lower bounder by the parent creation
            # * the upper boundary is not configurable and is always <now>
            _application_fees_refunds_request("parent_id").with_limit(100).with_starting_after("latest_refund_id").build(),
            _refunds_response().with_record(_a_refund()).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_multiple_application_fees_pages_when_read_then_query_pagination_on_parent(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _application_fees_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response()
            .with_pagination()
            .with_record(
                _an_application_fee()
                .with_id("parent_id")
                .with_field(
                    _REFUNDS_FIELD,
                    _as_dict(
                        _refunds_response()
                        .with_record(_a_refund())
                    )
                )
            ).build(),
        )
        http_mocker.get(
            _application_fees_request().with_starting_after("parent_id").with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response()
            .with_record(
                _an_application_fee()
                .with_field(
                    _REFUNDS_FIELD,
                    _as_dict(
                        _refunds_response()
                        .with_record(_a_refund())
                    )
                )
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_parent_stream_without_refund_when_read_then_stream_did_not_run(self, http_mocker: HttpMocker) -> None:
        # events stream is not validated as application fees is validated first
        http_mocker.get(
            _application_fees_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response().build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))
        assert_stream_did_not_run(output, _STREAM_NAME)

    @HttpMocker()
    def test_given_slice_range_when_read_then_perform_multiple_requests(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range

        http_mocker.get(
            _application_fees_request().with_created_gte(start_date).with_created_lte(slice_datetime).with_limit(100).build(),
            _application_fees_response().with_record(
                _an_application_fee()
                .with_field(_REFUNDS_FIELD, _as_dict(_refunds_response().with_record(_a_refund())))
            ).build(),
        )
        http_mocker.get(
            _application_fees_request().with_created_gte(slice_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response().with_record(
                _an_application_fee()
                .with_field(_REFUNDS_FIELD, _as_dict(_refunds_response().with_record(_a_refund())))
            ).build(),
        )

        output = self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_slice_range_and_refunds_pagination_when_read_then_do_not_slice_child(self, http_mocker: HttpMocker) -> None:
        """
        This means that if the user attempt to configure the slice range, it will only apply on the parent stream
        """
        start_date = _NOW - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range

        http_mocker.get(
            StripeRequestBuilder.application_fees_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_any_query_params().build(),
            _application_fees_response().build()
        )  # catching subsequent slicing request that we don't really care for this test
        http_mocker.get(
            _application_fees_request().with_created_gte(start_date).with_created_lte(slice_datetime).with_limit(100).build(),
            _application_fees_response().with_record(
                _an_application_fee()
                .with_id("parent_id")
                .with_field(
                    _REFUNDS_FIELD,
                    _as_dict(
                        _refunds_response()
                        .with_pagination()
                        .with_record(_a_refund().with_id("latest_refund_id"))
                    )
                )
            ).build(),
        )
        http_mocker.get(
            # slice range is not applied here
            _application_fees_refunds_request("parent_id").with_limit(100).with_starting_after("latest_refund_id").build(),
            _refunds_response().with_record(_a_refund()).build(),
        )

        self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))

        # request matched http_mocker

    @HttpMocker()
    def test_given_no_state_when_read_then_return_ignore_lookback(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _application_fees_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response().with_record(_an_application_fee()).build(),
        )

        self._read(_config().with_start_date(_A_START_DATE).with_lookback_window_in_days(10))

        # request matched http_mocker

    @HttpMocker()
    def test_given_one_page_when_read_then_cursor_field_is_set(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _application_fees_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response()
            .with_record(
                _an_application_fee()
                .with_field(
                    _REFUNDS_FIELD,
                    _as_dict(
                        _refunds_response()
                        .with_record(_a_refund())
                    )
                )
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert output.records[0].record.data["updated"] == output.records[0].record.data["created"]

    @HttpMocker()
    def test_given_http_status_401_when_read_then_config_error(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _application_fees_request().with_any_query_params().build(),
            a_response_with_status(401),
        )
        output = self._read(_config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error

    @HttpMocker()
    def test_given_rate_limited_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _application_fees_request().with_any_query_params().build(),
            [
                a_response_with_status(429),
                _application_fees_response().with_record(_an_application_fee().with_field(
                    _REFUNDS_FIELD,
                    _as_dict(
                        _refunds_response()
                        .with_record(_a_refund())
                    )
                )).build(),
            ],
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_when_read_then_raise_config_error(self, http_mocker: HttpMocker) -> None:
        request = _application_fees_request().with_any_query_params().build()
        http_mocker.get(
            request,
            a_response_with_status(500),
        )
        with patch.object(HttpStatusErrorHandler, 'max_retries', new=0):
            output = self._read(_config(), expecting_exception=True)
            # concurrent read processor handles exceptions as config errors after complete the max_retries
            assert output.errors[-1].trace.error.failure_type == FailureType.config_error

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):

    @HttpMocker()
    def test_given_no_state_when_read_then_use_application_fees_endpoint(self, http_mocker: HttpMocker) -> None:
        cursor_value = int(_A_START_DATE.timestamp()) + 1
        http_mocker.get(
            _application_fees_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _application_fees_response().with_record(
                _an_application_fee()
                .with_field(_REFUNDS_FIELD, _as_dict(_refunds_response().with_record(_a_refund().with_cursor(cursor_value))))
            ).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE), _NO_STATE)

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(updated=cursor_value)

    @HttpMocker()
    def test_given_state_when_read_then_query_events_using_types_and_state_value_plus_1(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=40)
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1

        http_mocker.get(
            _events_request().with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(
                _an_event().with_cursor(cursor_value).with_field(_DATA_FIELD, _a_refund().build())
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
        state_datetime = _NOW - timedelta(days=5)
        http_mocker.get(
            _events_request().with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_pagination().with_record(
                _an_event().with_id("last_record_id_from_first_page").with_field(_DATA_FIELD, _a_refund().build())
            ).build(),
        )
        http_mocker.get(
            _events_request().with_starting_after("last_record_id_from_first_page").with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(self._a_refund_event()).build(),
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

        http_mocker.get(
            _events_request().with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(slice_datetime).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(self._a_refund_event()).build(),
        )
        http_mocker.get(
            _events_request().with_created_gte(slice_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(self._a_refund_event()).with_record(self._a_refund_event()).build(),
        )

        output = self._read(
            _config().with_start_date(_NOW - timedelta(days=30)).with_slice_range_in_days(slice_range.days),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 3

    @HttpMocker()
    def test_given_state_earlier_than_30_days_when_read_then_query_events_using_types_and_event_lower_boundary(self, http_mocker: HttpMocker) -> None:
        # this seems odd as we would miss some data between start_date and events_lower_boundary. In that case, we should hit the
        # application fees endpoint
        start_date = _NOW - timedelta(days=40)
        state_value = _NOW - timedelta(days=39)
        events_lower_boundary = _NOW - timedelta(days=30)
        http_mocker.get(
            _events_request().with_created_gte(events_lower_boundary).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response().with_record(self._a_refund_event()).build(),
        )

        self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_value.timestamp())}).build(),
        )

        # request matched http_mocker

    def _a_refund_event(self) -> RecordBuilder:
        return _an_event().with_field(_DATA_FIELD, _a_refund().build())

    def _read(self, config: ConfigBuilder, state: Optional[Dict[str, Any]], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)
