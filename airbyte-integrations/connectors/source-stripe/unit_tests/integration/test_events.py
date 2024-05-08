# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.sources.source import TState
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
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

_STREAM_NAME = "events"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)
_SECOND_REQUEST = timedelta(seconds=1)
_THIRD_REQUEST = timedelta(seconds=2)


def _a_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _config() -> ConfigBuilder:
    return ConfigBuilder().with_start_date(_NOW - timedelta(days=73)).with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> SourceStripe:
    return SourceStripe(catalog, config, state)


def _a_record() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _a_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


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
            _a_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().with_record(_a_record()).with_record(_a_record()).build(),
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_many_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().with_pagination().with_record(_a_record().with_id("last_record_id_from_first_page")).build(),
        )
        http_mocker.get(
            _a_request().with_starting_after("last_record_id_from_first_page").with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().with_record(_a_record()).with_record(_a_record()).build(),
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 3

    @HttpMocker()
    def test_given_start_date_before_30_days_stripe_limit_and_slice_range_when_read_then_perform_request_before_30_days(self, http_mocker: HttpMocker) -> None:
        """
        This case is special because the source queries for a time range that is before 30 days. That being said as of 2023-12-13, the API
        mentions that "We only guarantee access to events through the Retrieve Event API for 30 days." (see
        https://stripe.com/docs/api/events)
        """
        start_date = _NOW - timedelta(days=61)
        slice_range = timedelta(days=30)
        slice_datetime = start_date + slice_range
        http_mocker.get(  # this first request has both gte and lte before 30 days even though we know there should not be records returned
            _a_request().with_created_gte(start_date).with_created_lte(slice_datetime).with_limit(100).build(),
            _a_response().build(),
        )
        http_mocker.get(
            _a_request().with_created_gte(slice_datetime + _SECOND_REQUEST).with_created_lte(slice_datetime + slice_range + _SECOND_REQUEST).with_limit(100).build(),
            _a_response().build(),
        )
        http_mocker.get(
            _a_request().with_created_gte(slice_datetime + slice_range + _THIRD_REQUEST).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().build(),
        )

        self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))

        # request matched http_mocker

    @HttpMocker()
    def test_given_lookback_window_when_read_then_request_before_start_date(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=30)
        lookback_window = timedelta(days=10)
        http_mocker.get(
            _a_request().with_created_gte(start_date - lookback_window).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().build(),
        )

        self._read(_config().with_start_date(start_date).with_lookback_window_in_days(lookback_window.days))

        # request matched http_mocker

    @HttpMocker()
    def test_given_slice_range_when_read_then_perform_multiple_requests(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range
        http_mocker.get(
            _a_request().with_created_gte(start_date).with_created_lte(slice_datetime).with_limit(100).build(),
            _a_response().build(),
        )
        http_mocker.get(
            _a_request().with_created_gte(slice_datetime + _SECOND_REQUEST).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().build(),
        )

        self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))

    @HttpMocker()
    def test_given_http_status_400_when_read_then_stream_is_ignored(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            a_response_with_status(400),
        )
        output = self._read(_config())
        assert len(output.get_stream_statuses(_STREAM_NAME)) == 0

    @HttpMocker()
    def test_given_http_status_401_when_read_then_stream_is_incomplete(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            a_response_with_status(401),
        )
        output = self._read(_config().with_start_date(_A_START_DATE), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.system_error

    @HttpMocker()
    def test_given_rate_limited_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            [
                a_response_with_status(429),
                _a_response().with_record(_a_record()).build(),
            ],
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_once_before_200_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            [a_response_with_status(500), _a_response().with_record(_a_record()).build()],
        )
        output = self._read(_config())
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_on_availability_when_read_then_raise_system_error(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            a_response_with_status(500),
        )
        output = self._read(_config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.system_error

    @HttpMocker()
    def test_when_read_then_validate_availability_for_full_refresh_and_incremental(self, http_mocker: HttpMocker) -> None:
        request = _a_request().with_any_query_params().build()
        http_mocker.get(
            request,
            _a_response().build(),
        )
        self._read(_config().with_start_date(_A_START_DATE))
        http_mocker.assert_number_of_calls(request, 3)  # one call for full_refresh availability, one call for incremental availability and one call for the actual read

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):

    @HttpMocker()
    def test_given_no_initial_state_when_read_then_return_state_based_on_cursor_field(self, http_mocker: HttpMocker) -> None:
        cursor_value = int(_A_START_DATE.timestamp()) + 1
        http_mocker.get(
            _a_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().with_record(_a_record().with_cursor(cursor_value)).build(),
        )
        output = self._read(_config().with_start_date(_A_START_DATE), _NO_STATE)
        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(created=int(_NOW.timestamp()))

    @HttpMocker()
    def test_given_state_when_read_then_use_state_for_query_params(self, http_mocker: HttpMocker) -> None:
        state_value = _A_START_DATE + timedelta(seconds=1)
        availability_check_requests = _a_request().with_any_query_params().build()
        http_mocker.get(
            availability_check_requests,
            _a_response().with_record(_a_record()).build(),
        )
        http_mocker.get(
            _a_request().with_created_gte(state_value + _AVOIDING_INCLUSIVE_BOUNDARIES).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().with_record(_a_record()).build(),
        )

        self._read(
            _config().with_start_date(_A_START_DATE),
            StateBuilder().with_stream_state("events", {"created": int(state_value.timestamp())}).build()
        )

        # request matched http_mocker

    @HttpMocker()
    def test_given_state_more_recent_than_cursor_when_read_then_return_state_based_on_cursor_field(self, http_mocker: HttpMocker) -> None:
        """
        We do not see exactly how this case can happen in a real life scenario but it is used to see if at least one state message
        would be populated given that no partitions were created.
        """
        cursor_value = int(_A_START_DATE.timestamp()) + 1
        more_recent_than_record_cursor = int(_NOW.timestamp()) - 1
        http_mocker.get(
            _a_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _a_response().with_record(_a_record().with_cursor(cursor_value)).build(),
        )

        output = self._read(
            _config().with_start_date(_A_START_DATE),
            StateBuilder().with_stream_state("events", {"created": more_recent_than_record_cursor}).build()
        )

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(created=more_recent_than_record_cursor)

    def _read(self, config: ConfigBuilder, state: Optional[Dict[str, Any]], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)
