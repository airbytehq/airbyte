#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

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


_STREAM_NAME = "invoice_line_items"
_ACCOUNT_ID = "acct_1G9HZLIEn49ers"
_CLIENT_SECRET = "ConfigBuilder default client secret"
_INVOICE_ID = "in_1K9GK0EcXtiJtvvhSo2LvGqT"
_NOW = datetime.now(timezone.utc)
_START_DATE = _NOW - timedelta(days=75)
_STATE_DATE = _NOW - timedelta(days=10)


def _config() -> ConfigBuilder:
    return ConfigBuilder().with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET).with_slice_range_in_days(365)


def _create_catalog(sync_mode: SyncMode = SyncMode.incremental) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(name=_STREAM_NAME, sync_mode=sync_mode).build()


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _invoice_lines_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.invoice_lines_endpoint(_INVOICE_ID, _ACCOUNT_ID, _CLIENT_SECRET)


def _line_item(line_item_id: str) -> Dict[str, Any]:
    return {
        "id": line_item_id,
        "object": "line_item",
        "amount": 1000,
        "currency": "usd",
        "invoice": _INVOICE_ID,
        "period": {"start": int(_STATE_DATE.timestamp()), "end": int(_STATE_DATE.timestamp())},
        "type": "invoiceitem",
    }


def _invoice(embedded_lines: List[Dict[str, Any]], has_more: bool, total_count: int) -> Dict[str, Any]:
    return {
        "id": _INVOICE_ID,
        "object": "invoice",
        "created": int(_STATE_DATE.timestamp()) + 1,
        "lines": {
            "object": "list",
            "data": embedded_lines,
            "has_more": has_more,
            "total_count": total_count,
            "url": f"/v1/invoices/{_INVOICE_ID}/lines",
        },
    }


def _event_record() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


def _invoice_created_event(invoice: Dict[str, Any]) -> RecordBuilder:
    return (
        _event_record()
        .with_field(FieldPath("type"), "invoice.created")
        .with_field(FieldPath("created"), int(_STATE_DATE.timestamp()) + 1)
        .with_field(NestedPath(["data", "object"]), invoice)
    )


def _invoice_line_record(line_item_id: str) -> RecordBuilder:
    return create_record_builder(
        find_template("invoice_lines", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
    ).with_id(line_item_id)


def _invoice_lines_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template("invoice_lines", __file__),
        records_path=FieldPath("data"),
        pagination_strategy=StripePaginationStrategy(),
    )


def _read_incremental(http_mocker: HttpMocker) -> Any:
    config = _config().with_start_date(_START_DATE).build()
    state = StateBuilder().with_stream_state(_STREAM_NAME, {"invoice_updated": int(_STATE_DATE.timestamp())}).build()
    source = get_source(config=config, state=state)
    return read(source, config=config, catalog=_create_catalog(), state=state)


@freezegun.freeze_time(_NOW.isoformat())
class InvoiceLineItemsIncrementalTest(TestCase):
    @HttpMocker()
    def test_given_truncated_embedded_lines_when_read_then_fetch_all_lines_from_invoice_endpoint(self, http_mocker: HttpMocker) -> None:
        all_line_ids = [f"il_{index}" for index in range(15)]
        embedded_lines = [_line_item(line_item_id) for line_item_id in all_line_ids[:10]]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _events_response().with_record(_invoice_created_event(_invoice(embedded_lines, has_more=True, total_count=15))).build(),
        )
        first_page = _invoice_lines_response()
        for line_item_id in all_line_ids[:10]:
            first_page = first_page.with_record(_invoice_line_record(line_item_id))
        second_page = _invoice_lines_response()
        for line_item_id in all_line_ids[10:]:
            second_page = second_page.with_record(_invoice_line_record(line_item_id))
        http_mocker.get(
            _invoice_lines_request().with_limit(100).build(),
            first_page.with_pagination().build(),
        )
        http_mocker.get(
            _invoice_lines_request().with_limit(100).with_starting_after("il_9").build(),
            second_page.build(),
        )

        output = _read_incremental(http_mocker)

        assert len(output.records) == 15
        assert sorted(record.record.data["id"] for record in output.records) == sorted(all_line_ids)
        assert all(record.record.data["invoice_id"] == _INVOICE_ID for record in output.records)

    @HttpMocker()
    def test_given_all_lines_embedded_when_read_then_extract_all_lines_without_extra_request(self, http_mocker: HttpMocker) -> None:
        all_line_ids = [f"il_{index}" for index in range(15)]
        embedded_lines = [_line_item(line_item_id) for line_item_id in all_line_ids]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _events_response().with_record(_invoice_created_event(_invoice(embedded_lines, has_more=False, total_count=15))).build(),
        )

        output = _read_incremental(http_mocker)

        assert len(output.records) == 15
        assert sorted(record.record.data["id"] for record in output.records) == sorted(all_line_ids)

    @HttpMocker()
    def test_given_few_embedded_lines_when_read_then_no_request_to_invoice_lines_endpoint(self, http_mocker: HttpMocker) -> None:
        all_line_ids = [f"il_{index}" for index in range(10)]
        embedded_lines = [_line_item(line_item_id) for line_item_id in all_line_ids]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _events_response().with_record(_invoice_created_event(_invoice(embedded_lines, has_more=False, total_count=10))).build(),
        )

        output = _read_incremental(http_mocker)

        assert len(output.records) == 10
        assert sorted(record.record.data["id"] for record in output.records) == sorted(all_line_ids)
