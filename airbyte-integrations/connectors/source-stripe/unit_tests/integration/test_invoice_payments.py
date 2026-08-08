#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalog, StreamDescriptor, SyncMode
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
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder


_STREAM_NAME = "invoice_payments"
_ENDPOINT_TEMPLATE_NAME = "invoice_payments"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_EVENT_TYPES = ["invoice_payment.paid"]
_DATA_FIELD = NestedPath(["data", "object"])


def _invoice_payments_request() -> StripeRequestBuilder:
    return StripeRequestBuilder._for_endpoint(_ENDPOINT_TEMPLATE_NAME, _ACCOUNT_ID, _CLIENT_SECRET).with_header(
        "Stripe-Version", "2025-03-31.basil"
    )


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_header("Stripe-Version", "2025-03-31.basil")


def _config() -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(_NOW - timedelta(days=75))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_slice_range_in_days(365)
    )


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _an_invoice_payment() -> RecordBuilder:
    return create_record_builder(
        find_template(_ENDPOINT_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _invoice_payments_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_ENDPOINT_TEMPLATE_NAME, __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy()
    )


def _an_event() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


def _read(config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[Dict[str, Any]] = None) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    return read(get_source(config, state), config, catalog, state)


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):
    @HttpMocker()
    def test_read_invoice_payments(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _invoice_payments_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _invoice_payments_response()
            .with_pagination()
            .with_record(_an_invoice_payment().with_id("last_record_id_from_first_page"))
            .build(),
        )
        http_mocker.get(
            _invoice_payments_request()
            .with_starting_after("last_record_id_from_first_page")
            .with_created_gte(_A_START_DATE)
            .with_created_lte(_NOW)
            .with_limit(100)
            .build(),
            _invoice_payments_response().with_record(_an_invoice_payment()).with_record(_an_invoice_payment()).build(),
        )

        output = _read(_config().with_start_date(_A_START_DATE), SyncMode.full_refresh)

        assert len(output.records) == 3
        assert output.records[0].record.data["id"] == "last_record_id_from_first_page"
        assert output.records[0].record.data["payment"]["payment_intent"] == "pi_3Q8e9rP2ZVFp9y3S1pmt4i3M"


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_use_invoice_payments_endpoint(self, http_mocker: HttpMocker) -> None:
        cursor_value = int(_A_START_DATE.timestamp()) + 1
        http_mocker.get(
            _invoice_payments_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _invoice_payments_response().with_record(_an_invoice_payment().with_cursor(cursor_value)).build(),
        )

        output = _read(_config().with_start_date(_A_START_DATE), SyncMode.incremental, {})

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state.updated == str(cursor_value)

    @HttpMocker()
    def test_given_state_when_read_then_query_events_using_types_and_state_value(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1
        http_mocker.get(
            _events_request().with_created_gte(state_datetime).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response()
            .with_record(_an_event().with_cursor(cursor_value).with_field(_DATA_FIELD, _an_invoice_payment().build()))
            .build(),
        )

        output = _read(
            _config(),
            SyncMode.incremental,
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 1
        assert output.records[0].record.data["payment"]["payment_intent"] == "pi_3Q8e9rP2ZVFp9y3S1pmt4i3M"
        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state.updated == str(cursor_value)

    @HttpMocker()
    def test_given_state_and_pagination_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        http_mocker.get(
            _events_request().with_created_gte(state_datetime).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response()
            .with_pagination()
            .with_record(_an_event().with_id("last_record_id_from_first_page").with_field(_DATA_FIELD, _an_invoice_payment().build()))
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
            _events_response().with_record(_an_event().with_field(_DATA_FIELD, _an_invoice_payment().build())).build(),
        )

        output = _read(
            _config(),
            SyncMode.incremental,
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 2
