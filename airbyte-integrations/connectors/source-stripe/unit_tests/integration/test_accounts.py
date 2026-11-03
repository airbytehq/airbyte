#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Union
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, StreamDescriptor, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder
from integration.accounts_windows import (
    NOW_2010,
    WINDOW_COUNT,
    created_inside_window,
    request_for_window,
    window_bounds,
    window_request,
    windows_from,
)
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder
from integration.response_builder import a_response_with_status


_STREAM_NAME = "accounts"
_ACCOUNT_ID = "acct_1G9HZLIEn49ers"
_CLIENT_SECRET = "ConfigBuilder default client secret"
_NOW = NOW_2010
_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID}
_NO_STATE = StateBuilder().build()
_A_START_DATE = datetime(2010, 1, 1, 0, 0, 0, 123456, tzinfo=timezone.utc)
_STATE_DATETIME = datetime(2010, 3, 5, tzinfo=timezone.utc)
_LOOKBACK_WINDOW_IN_DAYS = 3


def _create_config() -> ConfigBuilder:
    return ConfigBuilder().with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _config_2010() -> ConfigBuilder:
    return _create_config().with_start_date(_A_START_DATE)


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(name="accounts", sync_mode=sync_mode).build()


def _create_accounts_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.accounts_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _window_request(index: int) -> StripeRequestBuilder:
    return window_request(_create_accounts_request(), index)


def _incremental_request(start: datetime) -> StripeRequestBuilder:
    """The single window from `start` to the 2010 clock: a bookmark inside the last 30 days reads one window."""
    (window,) = windows_from(start)
    return request_for_window(_create_accounts_request(), *window)


def _create_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        pagination_strategy=StripePaginationStrategy(),
    )


def _create_record() -> RecordBuilder:
    return create_record_builder(
        find_template(_STREAM_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _a_page_with(*records: RecordBuilder) -> HttpResponse:
    response = _create_response()
    for record in records:
        response = response.with_record(record=record)
    return response.build()


def _mock_windows(http_mocker: HttpMocker, responses: Dict[int, Union[HttpResponse, List[HttpResponse]]]) -> List[HttpRequest]:
    """Registers the three windows the 2010 clock produces; windows without a response return an empty page."""
    requests = [_window_request(index).build() for index in range(WINDOW_COUNT)]
    for index, request in enumerate(requests):
        http_mocker.get(request, responses.get(index, _a_page_with()))
    return requests


def _a_state(updated: datetime) -> List[AirbyteStateMessage]:
    return StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(updated.timestamp())}).build()


def _read_incremental(config: Dict[str, Any], state: List[AirbyteStateMessage], expecting_exception: bool = False) -> EntrypointOutput:
    source = get_source(config=config, state=state)
    return read(source, config=config, catalog=_create_catalog(SyncMode.incremental), state=state, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class AccountsTest(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        created = created_inside_window(0)
        windows = _mock_windows(http_mocker, {0: _a_page_with(_create_record().with_cursor(created))})

        source = get_source(config=_CONFIG, state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 1
        for window in windows:
            http_mocker.assert_number_of_calls(window, 1)
        assert actual_messages.most_recent_state.stream_state.updated == str(created)

    @HttpMocker()
    def test_pagination(self, http_mocker: HttpMocker) -> None:
        created = created_inside_window(0)
        _mock_windows(
            http_mocker,
            {
                0: _create_response()
                .with_record(record=_create_record().with_id("last_record_id_from_first_page").with_cursor(created))
                .with_pagination()
                .build()
            },
        )
        http_mocker.get(
            _window_request(0).with_starting_after("last_record_id_from_first_page").build(),
            _a_page_with(_create_record().with_cursor(created)),
        )

        source = get_source(config=_CONFIG, state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 2

    @HttpMocker()
    def test_records_land_in_their_window_once(self, http_mocker: HttpMocker) -> None:
        windows = _mock_windows(
            http_mocker,
            {
                index: _a_page_with(_create_record().with_id(f"acct_window_{index}").with_cursor(created_inside_window(index)))
                for index in range(WINDOW_COUNT)
            },
        )

        source = get_source(config=_CONFIG, state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert sorted(record.record.data["id"] for record in actual_messages.records) == [
            f"acct_window_{index}" for index in range(WINDOW_COUNT)
        ]
        for window in windows:
            http_mocker.assert_number_of_calls(window, 1)
        assert actual_messages.most_recent_state.stream_state.updated == str(created_inside_window(WINDOW_COUNT - 1))

    @HttpMocker()
    def test_standard_account_without_created_gets_window_start(self, http_mocker: HttpMocker) -> None:
        standard_account = _create_record().with_id("acct_standard").build()
        standard_account.pop("created")
        standard_account["type"] = "standard"
        _mock_windows(http_mocker, {1: _a_page_with(RecordBuilder(standard_account, FieldPath("id"), None))})

        source = get_source(config=_CONFIG, state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 1
        assert actual_messages.records[0].record.data["id"] == "acct_standard"
        assert actual_messages.records[0].record.data["updated"] == int(window_bounds(1)[0].timestamp())


@freezegun.freeze_time(_NOW.isoformat())
class AccountsIncrementalTest(TestCase):
    """With state, the stream reads /v1/accounts from the bookmark minus the lookback window to now, in 30-day windows.

    Stripe files account.updated for connected accounts in the connected account's own event feed, so a Connect
    platform's /v1/events never carries them. HttpMocker fails these tests if any other request is made.
    """

    @HttpMocker()
    def test_given_state_when_read_then_query_accounts_endpoint_with_created_window(self, http_mocker: HttpMocker) -> None:
        record_created = int(datetime(2010, 3, 10, tzinfo=timezone.utc).timestamp())
        http_mocker.get(_incremental_request(_STATE_DATETIME).build(), _a_page_with(_create_record().with_cursor(record_created)))

        output = _read_incremental(_config_2010().build(), _a_state(_STATE_DATETIME))

        assert len(output.records) == 1
        assert output.records[0].record.data["updated"] == record_created
        assert output.most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert output.most_recent_state.stream_state.updated == str(record_created)

    @HttpMocker()
    def test_given_state_and_lookback_window_when_read_then_created_gte_is_state_minus_lookback(self, http_mocker: HttpMocker) -> None:
        record_created = int(datetime(2010, 3, 3, tzinfo=timezone.utc).timestamp())
        http_mocker.get(
            _incremental_request(_STATE_DATETIME - timedelta(days=_LOOKBACK_WINDOW_IN_DAYS)).build(),
            _a_page_with(_create_record().with_cursor(record_created)),
        )

        output = _read_incremental(_config_2010().with_lookback_window_in_days(_LOOKBACK_WINDOW_IN_DAYS).build(), _a_state(_STATE_DATETIME))

        assert len(output.records) == 1
        assert output.most_recent_state.stream_state.updated == str(int(_STATE_DATETIME.timestamp()))

    @HttpMocker()
    def test_given_state_and_no_new_accounts_when_read_then_state_is_unchanged(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_incremental_request(_STATE_DATETIME).build(), _a_page_with())

        output = _read_incremental(_config_2010().build(), _a_state(_STATE_DATETIME))

        assert len(output.records) == 0
        assert output.most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert output.most_recent_state.stream_state.updated == str(int(_STATE_DATETIME.timestamp()))

    @HttpMocker()
    def test_given_state_and_pagination_when_read_then_return_records_from_all_pages(self, http_mocker: HttpMocker) -> None:
        first_record_created = int(datetime(2010, 3, 8, tzinfo=timezone.utc).timestamp())
        second_record_created = int(datetime(2010, 3, 12, tzinfo=timezone.utc).timestamp())
        http_mocker.get(
            _incremental_request(_STATE_DATETIME).build(),
            _create_response()
            .with_record(record=_create_record().with_id("last_record_id_from_first_page").with_cursor(first_record_created))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            _incremental_request(_STATE_DATETIME).with_starting_after("last_record_id_from_first_page").build(),
            _a_page_with(_create_record().with_cursor(second_record_created)),
        )

        output = _read_incremental(_config_2010().build(), _a_state(_STATE_DATETIME))

        assert len(output.records) == 2
        assert output.most_recent_state.stream_state.updated == str(second_record_created)

    @HttpMocker()
    def test_failed_window_then_retry_resumes_from_checkpoint(self, http_mocker: HttpMocker) -> None:
        checkpoint = datetime(2010, 1, 10, tzinfo=timezone.utc)
        first_windows = _mock_windows(
            http_mocker,
            {
                0: _a_page_with(_create_record().with_id("acct_before_failure").with_cursor(int(checkpoint.timestamp()))),
                1: a_response_with_status(401),
            },
        )

        first_attempt = _read_incremental(_config_2010().build(), _NO_STATE, expecting_exception=True)

        assert first_attempt.errors
        assert first_attempt.state_messages[-1].state.stream.stream_state.updated == str(int(checkpoint.timestamp()))
        for request in first_windows:
            http_mocker.assert_number_of_calls(request, 1)

        retry_windows = windows_from(checkpoint)
        assert retry_windows == [
            (checkpoint, datetime(2010, 2, 8, 23, 59, 59, tzinfo=timezone.utc)),
            (datetime(2010, 2, 9, tzinfo=timezone.utc), datetime(2010, 3, 10, 23, 59, 59, tzinfo=timezone.utc)),
            (datetime(2010, 3, 11, tzinfo=timezone.utc), datetime(2010, 3, 15, 12, 0, 0, tzinfo=timezone.utc)),
        ]
        created_in_failed_region = int(datetime(2010, 2, 14, tzinfo=timezone.utc).timestamp())
        retry_requests = [request_for_window(_create_accounts_request(), start, end).build() for start, end in retry_windows]
        # created[gte] is inclusive, so the checkpoint record comes back with the retry.
        http_mocker.get(
            retry_requests[0], _a_page_with(_create_record().with_id("acct_before_failure").with_cursor(int(checkpoint.timestamp())))
        )
        http_mocker.get(
            retry_requests[1], _a_page_with(_create_record().with_id("acct_in_failed_region").with_cursor(created_in_failed_region))
        )
        http_mocker.get(retry_requests[2], _a_page_with())

        retry = _read_incremental(_config_2010().build(), _a_state(checkpoint))

        assert not retry.errors
        assert sorted(record.record.data["id"] for record in retry.records) == ["acct_before_failure", "acct_in_failed_region"]
        for request in retry_requests:
            http_mocker.assert_number_of_calls(request, 1)
        assert retry.most_recent_state.stream_state.updated == str(created_in_failed_region)
