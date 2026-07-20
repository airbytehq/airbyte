#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
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


_STREAM_NAME = "invoices"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"

# Minimum overlap enforced on the events-based incremental path (see manifest `events_read_slice_cursor`).
_EVENTS_LOOKBACK_FLOOR = timedelta(days=7)

_INVOICE_EVENT_TYPES: List[str] = [
    "invoice.created",
    "invoice.deleted",
    "invoice.finalization_failed",
    "invoice.finalized",
    "invoice.marked_uncollectible",
    "invoice.overdue",
    "invoice.paid",
    "invoice.payment_action_required",
    "invoice.payment_failed",
    "invoice.payment_succeeded",
    "invoice.sent",
    "invoice.updated",
    "invoice.voided",
    "invoice.will_be_due",
]


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _config() -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(_A_START_DATE)
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_slice_range_in_days(365)
    )


def _catalog() -> Any:
    return CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()


def _an_events_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


def _an_event_record() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _state(updated: datetime) -> Dict[str, Any]:
    return StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(updated.timestamp())}).build()


def _read(config: ConfigBuilder, state: Optional[Dict[str, Any]], expecting_exception: bool = False) -> EntrypointOutput:
    catalog = _catalog()
    built_config = config.build()
    return read(get_source(built_config, state), built_config, catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class InvoicesIncrementalLookbackTest(TestCase):
    """The invoices stream captures status changes only through the Events API on incremental syncs.

    Because Stripe invoices have no native `updated` field, a mutation (e.g. draft -> paid) never advances
    the entity cursor; it is only observable as an `invoice.*` event. Without an overlap window, events
    emitted after the entity snapshot or near a sync boundary can be silently dropped. These tests pin the
    minimum lookback applied on the events-based incremental path (oncall #12975).
    """

    @HttpMocker()
    def test_given_state_when_read_then_events_request_applies_lookback_floor(self, http_mocker: HttpMocker) -> None:
        state_updated = _NOW - timedelta(days=15)
        expected_gte = state_updated - _EVENTS_LOOKBACK_FLOOR

        http_mocker.get(
            _events_request()
            .with_created_gte(expected_gte)
            .with_created_lte(_NOW)
            .with_limit(100)
            .with_types(_INVOICE_EVENT_TYPES)
            .build(),
            _an_events_response().build(),
        )

        self._assert_no_error(_read(_config(), _state(state_updated)))

    @HttpMocker()
    def test_given_lookback_window_larger_than_floor_when_read_then_config_wins(self, http_mocker: HttpMocker) -> None:
        state_updated = _NOW - timedelta(days=10)
        configured_lookback = timedelta(days=14)
        expected_gte = state_updated - configured_lookback

        http_mocker.get(
            _events_request()
            .with_created_gte(expected_gte)
            .with_created_lte(_NOW)
            .with_limit(100)
            .with_types(_INVOICE_EVENT_TYPES)
            .build(),
            _an_events_response().build(),
        )

        self._assert_no_error(_read(_config().with_lookback_window_in_days(configured_lookback.days), _state(state_updated)))

    @staticmethod
    def _assert_no_error(output: EntrypointOutput) -> None:
        assert not output.errors, output.errors
