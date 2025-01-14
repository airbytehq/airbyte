# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from unittest import TestCase

import freezegun
from source_stripe import SourceStripe

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
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
_CONFIG = {
    "client_secret": _CLIENT_SECRET,
    "account_id": _ACCOUNT_ID,
}
_NO_STATE = StateBuilder().build()
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)


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
    )


@freezegun.freeze_time(_NOW.isoformat())
class AccountsTest(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record()).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
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

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert len(actual_messages.records) == 2
