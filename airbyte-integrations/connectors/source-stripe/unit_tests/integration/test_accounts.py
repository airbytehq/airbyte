#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
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


_STREAM_NAME = "accounts"
_EVENT_TYPES = [
    "account.updated",
    "account.external_account.created",
    "account.external_account.updated",
    "account.external_account.deleted",
]
_DATA_FIELD = NestedPath(["data", "object"])
_ACCOUNT_ID = "acct_1G9HZLIEn49ers"
_CLIENT_SECRET = "ConfigBuilder default client secret"
_NOW = datetime.now(timezone.utc)
_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID}
_NO_STATE = StateBuilder().build()
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)


def _create_config() -> ConfigBuilder:
    return ConfigBuilder().with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(name="accounts", sync_mode=sync_mode).build()


def _create_accounts_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.accounts_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _create_account_request(account_id: str) -> StripeRequestBuilder:
    return StripeRequestBuilder._for_endpoint(f"accounts/{account_id}", _ACCOUNT_ID, _CLIENT_SECRET)


def _create_events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


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
    )


def _create_events_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template("events", __file__),
        records_path=FieldPath("data"),
        pagination_strategy=StripePaginationStrategy(),
    )


def _create_event_record() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


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

    @HttpMocker()
    def test_incremental_hydrated_mode_refreshes_account_from_detail_endpoint(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1
        account = _create_record().with_id("acct_hydrated").build()

        http_mocker.get(
            _create_events_request()
            .with_created_gte(state_datetime)
            .with_created_lte(_NOW)
            .with_limit(100)
            .with_types(_EVENT_TYPES)
            .build(),
            _create_events_response()
            .with_record(_create_event_record().with_cursor(cursor_value).with_field(_DATA_FIELD, account))
            .build(),
        )
        http_mocker.get(
            _create_account_request("acct_hydrated").build(),
            HttpResponse(json.dumps(account), 200),
        )

        config = (
            _create_config().with_start_date(_NOW - timedelta(days=75)).with_event_based_incremental_sync_mode("hydrated_events").build()
        )
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        source = get_source(config=config, state=state)
        actual_messages = read(source, config=config, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)

        assert len(actual_messages.records) == 1
        assert actual_messages.records[0].record.data["id"] == "acct_hydrated"
        assert actual_messages.records[0].record.data["updated"] == cursor_value
