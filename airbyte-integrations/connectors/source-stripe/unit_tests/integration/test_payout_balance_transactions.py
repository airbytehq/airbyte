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


_STREAM_NAME = "payout_balance_transactions"
_A_PAYOUT_ID = "a_payout_id"
_ANOTHER_PAYOUT_ID = "another_payout_id"
_ACCOUNT_ID = "acct_1G9HZLIEn49ers"
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)
_CLIENT_SECRET = "ConfigBuilder default client secret"
_NOW = datetime.now(timezone.utc)
_START_DATE = _NOW - timedelta(days=75)
_STATE_DATE = _NOW - timedelta(days=10)
_NO_STATE = StateBuilder().build()
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)

_DATA_FIELD = NestedPath(["data", "object"])
_EVENT_TYPES = [
    "payout.canceled",
    "payout.created",
    "payout.failed",
    "payout.paid",
    "payout.reconciliation_completed",
    "payout.updated",
]


def _config() -> ConfigBuilder:
    return ConfigBuilder().with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(name=_STREAM_NAME, sync_mode=sync_mode).build()


def _balance_transactions_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.balance_transactions_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _payouts_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.payouts_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _balance_transaction_record() -> RecordBuilder:
    return create_record_builder(
        find_template("balance_transactions", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
    )


def _balance_transactions_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template("balance_transactions", __file__),
        records_path=FieldPath("data"),
        pagination_strategy=StripePaginationStrategy(),
    )


def _event_record() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


def _create_payout_record() -> RecordBuilder:
    return create_record_builder(
        find_template("payouts", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
    )


def _payouts_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template("payouts", __file__),
        records_path=FieldPath("data"),
        pagination_strategy=StripePaginationStrategy(),
    )


@freezegun.freeze_time(_NOW.isoformat())
class PayoutBalanceTransactionsFullRefreshTest(TestCase):
    @HttpMocker()
    def test_given_multiple_parents_when_read_then_extract_from_all_children(self, http_mocker: HttpMocker) -> None:
        config = _config().with_start_date(_START_DATE).build()
        http_mocker.get(
            _payouts_request().with_created_gte(_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _payouts_response()
            .with_record(_create_payout_record().with_id(_A_PAYOUT_ID))
            .with_record(_create_payout_record().with_id(_ANOTHER_PAYOUT_ID))
            .build(),
        )
        http_mocker.get(
            _balance_transactions_request().with_limit(100).with_payout(_A_PAYOUT_ID).build(),
            _balance_transactions_response().with_record(_balance_transaction_record()).build(),
        )
        http_mocker.get(
            _balance_transactions_request().with_limit(100).with_payout(_ANOTHER_PAYOUT_ID).build(),
            _balance_transactions_response().with_record(_balance_transaction_record()).with_record(_balance_transaction_record()).build(),
        )

        source = SourceStripe(config=config, catalog=_create_catalog(), state=_NO_STATE)
        output = read(source, config=config, catalog=_create_catalog())

        assert len(output.records) == 3

    @HttpMocker()
    def test_when_read_then_add_payout_field(self, http_mocker: HttpMocker) -> None:
        config = _config().with_start_date(_START_DATE).build()
        http_mocker.get(
            _payouts_request().with_created_gte(_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _payouts_response().with_record(_create_payout_record().with_id(_A_PAYOUT_ID)).build(),
        )
        http_mocker.get(
            _balance_transactions_request().with_limit(100).with_payout(_A_PAYOUT_ID).build(),
            _balance_transactions_response().with_record(_balance_transaction_record()).build(),
        )

        source = SourceStripe(config=config, catalog=_create_catalog(), state=_NO_STATE)
        output = read(source, config=config, catalog=_create_catalog())

        assert output.records[0].record.data["payout"]


@freezegun.freeze_time(_NOW.isoformat())
class PayoutBalanceTransactionsIncrementalTest(TestCase):
    @HttpMocker()
    def test_when_read_then_fetch_from_updated_payouts(self, http_mocker: HttpMocker) -> None:
        config = _config().with_start_date(_START_DATE).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(_STATE_DATE.timestamp())}).build()
        catalog = _create_catalog(SyncMode.incremental)
        http_mocker.get(
            _events_request()
            .with_created_gte(_STATE_DATE + _AVOIDING_INCLUSIVE_BOUNDARIES)
            .with_created_lte(_NOW)
            .with_limit(100)
            .with_types(_EVENT_TYPES)
            .build(),
            _events_response()
            .with_record(_event_record().with_field(_DATA_FIELD, _create_payout_record().with_id(_A_PAYOUT_ID).build()))
            .build(),
        )
        http_mocker.get(
            _balance_transactions_request().with_limit(100).with_payout(_A_PAYOUT_ID).build(),
            _balance_transactions_response().with_record(_balance_transaction_record()).build(),
        )

        source = SourceStripe(config=config, catalog=catalog, state=state)
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
