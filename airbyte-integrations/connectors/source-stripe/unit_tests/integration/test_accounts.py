#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, StreamDescriptor, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder


_STREAM_NAME = "accounts"
_ACCOUNT_ID = "acct_1G9HZLIEn49ers"
_CLIENT_SECRET = "ConfigBuilder default client secret"
_NOW = datetime.now(timezone.utc)
_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID}
_NO_STATE = StateBuilder().build()
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)
_A_START_DATE = _NOW - timedelta(days=30)
_STATE_DATETIME = _NOW - timedelta(days=5)
_LOOKBACK_WINDOW_IN_DAYS = 7


def _create_config() -> ConfigBuilder:
    return ConfigBuilder().with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(name="accounts", sync_mode=sync_mode).build()


def _create_accounts_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.accounts_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


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


def _create_state(state_datetime: datetime) -> List[AirbyteStateMessage]:
    return StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()


def _read_incremental(config: Dict[str, Any], state: List[AirbyteStateMessage]) -> EntrypointOutput:
    source = get_source(config=config, state=state)
    return read(source, config=config, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)


@freezegun.freeze_time(_NOW.isoformat())
class AccountsTest(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record()).build(),
        )

        source = get_source(config=_CONFIG, state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 1

    @HttpMocker()
    def test_pagination(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record().with_id("last_record_id_from_first_page")).with_pagination().build(),
        )
        http_mocker.get(
            _create_accounts_request().with_limit(100).with_starting_after("last_record_id_from_first_page").build(),
            _create_response().with_record(record=_create_record()).build(),
        )

        source = get_source(config=_CONFIG, state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 2


@freezegun.freeze_time(_NOW.isoformat())
class AccountsIncrementalTest(TestCase):
    """With state, the stream reads /v1/accounts by created window instead of the platform's /v1/events feed.

    Stripe files account.updated for connected accounts in the connected account's own event feed, so a Connect
    platform's events feed never carries them. HttpMocker fails these tests if any other request is made.
    """

    @HttpMocker()
    def test_given_state_when_read_then_query_accounts_endpoint_with_created_window(self, http_mocker: HttpMocker) -> None:
        record_created = int((_NOW - timedelta(days=2)).timestamp())
        http_mocker.get(
            _create_accounts_request().with_created_gte(_STATE_DATETIME).with_created_lte(_NOW).with_limit(100).build(),
            _create_response().with_record(record=_create_record().with_cursor(record_created)).build(),
        )

        config = _create_config().with_start_date(_A_START_DATE).build()
        output = _read_incremental(config, _create_state(_STATE_DATETIME))

        assert len(output.records) == 1
        assert output.records[0].record.data["updated"] == record_created
        assert output.most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert output.most_recent_state.stream_state.updated == str(record_created)

    @HttpMocker()
    def test_given_state_and_lookback_window_when_read_then_created_gte_is_state_minus_lookback(self, http_mocker: HttpMocker) -> None:
        record_created = int((_NOW - timedelta(days=10)).timestamp())
        http_mocker.get(
            _create_accounts_request()
            .with_created_gte(_STATE_DATETIME - timedelta(days=_LOOKBACK_WINDOW_IN_DAYS))
            .with_created_lte(_NOW)
            .with_limit(100)
            .build(),
            _create_response().with_record(record=_create_record().with_cursor(record_created)).build(),
        )

        config = _create_config().with_start_date(_A_START_DATE).with_lookback_window_in_days(_LOOKBACK_WINDOW_IN_DAYS).build()
        output = _read_incremental(config, _create_state(_STATE_DATETIME))

        assert len(output.records) == 1
        assert output.most_recent_state.stream_state.updated == str(int(_STATE_DATETIME.timestamp()))

    @HttpMocker()
    def test_given_state_and_no_new_accounts_when_read_then_state_is_unchanged(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_created_gte(_STATE_DATETIME).with_created_lte(_NOW).with_limit(100).build(),
            _create_response().build(),
        )

        config = _create_config().with_start_date(_A_START_DATE).build()
        output = _read_incremental(config, _create_state(_STATE_DATETIME))

        assert len(output.records) == 0
        assert output.most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert output.most_recent_state.stream_state.updated == str(int(_STATE_DATETIME.timestamp()))

    @HttpMocker()
    def test_given_state_and_pagination_when_read_then_return_records_from_all_pages(self, http_mocker: HttpMocker) -> None:
        first_record_created = int((_NOW - timedelta(days=3)).timestamp())
        second_record_created = int((_NOW - timedelta(days=1)).timestamp())
        http_mocker.get(
            _create_accounts_request().with_created_gte(_STATE_DATETIME).with_created_lte(_NOW).with_limit(100).build(),
            _create_response()
            .with_record(record=_create_record().with_id("last_record_id_from_first_page").with_cursor(first_record_created))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            _create_accounts_request()
            .with_created_gte(_STATE_DATETIME)
            .with_created_lte(_NOW)
            .with_limit(100)
            .with_starting_after("last_record_id_from_first_page")
            .build(),
            _create_response().with_record(record=_create_record().with_cursor(second_record_created)).build(),
        )

        config = _create_config().with_start_date(_A_START_DATE).build()
        output = _read_incremental(config, _create_state(_STATE_DATETIME))

        assert len(output.records) == 2
        assert output.most_recent_state.stream_state.updated == str(second_record_created)
