#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
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


def _legacy_invoice_event(
    event_type: str,
    api_version: str,
    invoice_id: str,
    created_offset: int,
    lines: list[dict[str, Any]],
    has_more: bool = False,
    total_count: int | None = None,
) -> Dict[str, Any]:
    created = int(_STATE_DATE.timestamp()) + created_offset
    return {
        "id": f"evt_{invoice_id}_{created_offset}",
        "object": "event",
        "api_version": api_version,
        "created": created,
        "type": event_type,
        "data": {
            "object": {
                "id": invoice_id,
                "object": "invoice",
                "created": created,
                "lines": {
                    "object": "list",
                    "data": lines,
                    "has_more": has_more,
                    "total_count": len(lines) if total_count is None else total_count,
                    "url": f"/v1/invoices/{invoice_id}/lines",
                },
            }
        },
    }


def _raw_list_response(records: list[dict[str, Any]], status: int = 200) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "data": records, "has_more": False}), status)


def _raw_invoice_lines_request(invoice_id: str) -> StripeRequestBuilder:
    return StripeRequestBuilder.invoice_lines_endpoint(invoice_id, _ACCOUNT_ID, _CLIENT_SECRET).with_limit(100)


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


@freezegun.freeze_time(_NOW.isoformat())
class InvoiceLineItemsLegacyApiVersionTest(TestCase):
    @HttpMocker()
    def test_2018_event_remaps_ii_and_sub_ids_and_backfills_subscription(self, http_mocker: HttpMocker) -> None:
        lines = [
            {
                "id": "ii_A1",
                "unique_id": "il_A1",
                "object": "line_item",
                "amount": 1000,
                "currency": "usd",
                "type": "invoiceitem",
                "subscription": "sub_S",
            },
            {
                "id": "sub_S",
                "unique_id": "il_A2",
                "unique_line_item_id": "sli_A2",
                "object": "line_item",
                "amount": 1000,
                "currency": "usd",
                "type": "subscription",
                "subscription": None,
            },
        ]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _raw_list_response([_legacy_invoice_event("invoice.updated", "2018-02-28", "in_A", 1, lines)]),
        )

        output = _read_incremental(http_mocker)
        records = [record.record.data for record in output.records]
        by_id = {record["id"]: record for record in records}

        assert set(by_id) == {"il_A1", "il_A2"}
        assert by_id["il_A1"]["subscription"] == "sub_S"
        assert by_id["il_A2"]["subscription"] == "sub_S"
        assert all(record["invoice_id"] == "in_A" for record in records)
        assert all(isinstance(record["invoice_updated"], int) for record in records)
        assert all(not {"unique_id", "unique_line_item_id", "original_record"} & record.keys() for record in records)

    @HttpMocker()
    def test_2018_renewal_pair_sub_collision_yields_distinct_ids(self, http_mocker: HttpMocker) -> None:
        events = [
            _legacy_invoice_event(
                "invoice.updated",
                "2018-02-28",
                invoice_id,
                offset,
                [
                    {
                        "id": "sub_S",
                        "unique_id": line_id,
                        "object": "line_item",
                        "amount": 1000,
                        "currency": "usd",
                        "type": "subscription",
                        "subscription": None,
                    }
                ],
            )
            for invoice_id, offset, line_id in [("in_C1", 1, "il_C1"), ("in_C2", 2, "il_C2")]
        ]
        http_mocker.get(_events_request().with_any_query_params().build(), _raw_list_response(events))

        output = _read_incremental(http_mocker)
        by_id = {record.record.data["id"]: record.record.data for record in output.records}

        assert set(by_id) == {"il_C1", "il_C2"}
        assert by_id["il_C1"]["invoice_id"] == "in_C1"
        assert by_id["il_C2"]["invoice_id"] == "in_C2"
        assert all(record["subscription"] == "sub_S" for record in by_id.values())

    @HttpMocker()
    def test_2019_sli_line_remapped_subscription_untouched(self, http_mocker: HttpMocker) -> None:
        lines = [
            {
                "id": "sli_B1",
                "unique_id": "il_B1",
                "object": "line_item",
                "amount": 1000,
                "currency": "usd",
                "type": "subscription",
                "subscription": "sub_S",
            }
        ]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _raw_list_response([_legacy_invoice_event("invoice.updated", "2019-11-05", "in_B", 1, lines)]),
        )

        output = _read_incremental(http_mocker)
        record = output.records[0].record.data

        assert record["id"] == "il_B1"
        assert record["subscription"] == "sub_S"
        assert "unique_id" not in record

    @HttpMocker()
    def test_modern_event_is_noop(self, http_mocker: HttpMocker) -> None:
        lines = [
            {
                "id": "il_D1",
                "object": "line_item",
                "amount": 1000,
                "currency": "usd",
                "type": "subscription",
                "subscription": "sub_S",
            },
            {
                "id": "il_D2",
                "object": "line_item",
                "amount": 500,
                "currency": "usd",
                "type": "invoiceitem",
                "subscription": None,
            },
        ]
        created = int(_STATE_DATE.timestamp()) + 1
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _raw_list_response([_legacy_invoice_event("invoice.updated", "2025-03-31.basil", "in_D", 1, lines)]),
        )

        output = _read_incremental(http_mocker)
        by_id = {record.record.data["id"]: record.record.data for record in output.records}

        assert by_id == {
            line["id"]: {
                **{key: value for key, value in line.items() if value is not None},
                "invoice_id": "in_D",
                "invoice_updated": created,
            }
            for line in lines
        }
        assert "subscription" not in by_id["il_D2"]

    @HttpMocker()
    def test_truncated_legacy_event_uses_refetched_lines_unchanged(self, http_mocker: HttpMocker) -> None:
        embedded_lines = [
            {
                "id": f"ii_T{index}",
                "unique_id": f"il_T{index}",
                "object": "line_item",
                "amount": 100,
                "currency": "usd",
                "type": "invoiceitem",
            }
            for index in range(10)
        ]
        modern_lines = [
            {
                "id": f"il_T{index}",
                "object": "line_item",
                "amount": 100,
                "currency": "usd",
                "type": "invoiceitem",
                "invoice": "in_T",
            }
            for index in range(12)
        ]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _raw_list_response(
                [_legacy_invoice_event("invoice.updated", "2018-02-28", "in_T", 1, embedded_lines, has_more=True, total_count=12)]
            ),
        )
        http_mocker.get(_raw_invoice_lines_request("in_T").build(), _raw_list_response(modern_lines))

        output = _read_incremental(http_mocker)
        records = [record.record.data for record in output.records]

        assert {record["id"] for record in records} == {f"il_T{index}" for index in range(12)}
        assert len(records) == 12
        assert all(record["invoice_id"] == "in_T" for record in records)
        assert all("unique_id" not in record for record in records)

    @HttpMocker()
    def test_deleted_invoice_404_falls_back_to_remapped_embedded_lines(self, http_mocker: HttpMocker) -> None:
        lines = [
            {
                "id": "ii_F1",
                "unique_id": "il_F1",
                "object": "line_item",
                "amount": 1000,
                "currency": "usd",
                "type": "invoiceitem",
            },
            {
                "id": "sub_S",
                "unique_id": "il_F2",
                "object": "line_item",
                "amount": 1000,
                "currency": "usd",
                "type": "subscription",
                "subscription": None,
            },
        ]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _raw_list_response([_legacy_invoice_event("invoice.deleted", "2018-02-28", "in_F", 1, lines, has_more=True)]),
        )
        http_mocker.get(
            _raw_invoice_lines_request("in_F").build(),
            HttpResponse(json.dumps({"error": {"message": "No such invoice: 'in_F'"}}), 404),
        )

        output = _read_incremental(http_mocker)
        by_id = {record.record.data["id"]: record.record.data for record in output.records}

        assert set(by_id) == {"il_F1", "il_F2"}
        assert all(record["is_deleted"] is True for record in by_id.values())
        assert by_id["il_F2"]["subscription"] == "sub_S"

    @HttpMocker()
    def test_missing_or_null_unique_id_leaves_record_unchanged(self, http_mocker: HttpMocker) -> None:
        lines = [
            {"id": "ii_X1", "object": "line_item", "type": "invoiceitem"},
            {"id": "ii_X2", "unique_id": None, "object": "line_item", "type": "invoiceitem"},
            {"id": "sub_X", "object": "line_item", "type": "subscription", "subscription": None},
        ]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _raw_list_response([_legacy_invoice_event("invoice.updated", "2018-02-28", "in_X", 1, lines)]),
        )

        output = _read_incremental(http_mocker)
        by_id = {record.record.data["id"]: record.record.data for record in output.records}

        assert set(by_id) == {"ii_X1", "ii_X2", "sub_X"}
        assert by_id["sub_X"].get("subscription") is None
        assert all("unique_id" not in record for record in by_id.values())

    @HttpMocker()
    def test_subscription_backfill_requires_sub_prefix(self, http_mocker: HttpMocker) -> None:
        lines = [
            {
                "id": "ii_Y1",
                "unique_id": "il_Y1",
                "object": "line_item",
                "amount": 1000,
                "currency": "usd",
                "type": "subscription",
                "subscription": None,
            }
        ]
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _raw_list_response([_legacy_invoice_event("invoice.updated", "2018-02-28", "in_Y", 1, lines)]),
        )

        output = _read_incremental(http_mocker)
        record = output.records[0].record.data

        assert record["id"] == "il_Y1"
        assert record.get("subscription") is None

    @HttpMocker()
    def test_legacy_invoice_full_refresh_and_incremental_emit_same_line_ids(self, http_mocker: HttpMocker) -> None:
        created = int(_STATE_DATE.timestamp()) + 1
        period = {"start": created, "end": created + 3600}
        modern_lines = [
            {
                "id": "il_L1",
                "object": "line_item",
                "amount": 1000,
                "currency": "usd",
                "type": "invoiceitem",
                "livemode": False,
                "period": period,
                "subscription": "sub_S",
                "invoice": "in_L",
            },
            {
                "id": "il_L2",
                "object": "line_item",
                "amount": 2000,
                "currency": "usd",
                "type": "subscription",
                "livemode": False,
                "period": period,
                "subscription": "sub_S",
                "invoice": "in_L",
            },
        ]
        invoice = {
            "id": "in_L",
            "object": "invoice",
            "created": created,
            "updated": created + 1,
            "lines": {
                "object": "list",
                "data": modern_lines,
                "has_more": False,
                "total_count": 2,
                "url": "/v1/invoices/in_L/lines",
            },
        }
        invoices_request = StripeRequestBuilder("invoices", _ACCOUNT_ID, _CLIENT_SECRET).with_any_query_params().build()
        http_mocker.get(invoices_request, _raw_list_response([invoice]))
        http_mocker.get(
            _events_request().with_any_query_params().build(),
            _raw_list_response(
                [
                    _legacy_invoice_event(
                        "invoice.updated",
                        "2018-02-28",
                        "in_L",
                        1,
                        [
                            {
                                "id": "ii_L1",
                                "unique_id": "il_L1",
                                "object": "line_item",
                                "amount": 1000,
                                "currency": "usd",
                                "type": "invoiceitem",
                                "livemode": False,
                                "period": period,
                                "subscription": "sub_S",
                            },
                            {
                                "id": "sub_S",
                                "unique_id": "il_L2",
                                "unique_line_item_id": "sli_L2",
                                "object": "line_item",
                                "amount": 2000,
                                "currency": "usd",
                                "type": "subscription",
                                "livemode": False,
                                "period": period,
                                "subscription": None,
                            },
                        ],
                    )
                ]
            ),
        )

        config = _config().with_start_date(_START_DATE).build()
        full_refresh_source = get_source(config=config)
        full_refresh_output = read(full_refresh_source, config=config, catalog=_create_catalog(SyncMode.full_refresh))
        incremental_output = _read_incremental(http_mocker)
        full_refresh_records = [record.record.data for record in full_refresh_output.records]
        incremental_records = [record.record.data for record in incremental_output.records]
        full_refresh_by_id = {record["id"]: record for record in full_refresh_records}
        incremental_by_id = {record["id"]: record for record in incremental_records}

        assert set(full_refresh_by_id) == set(incremental_by_id) == {"il_L1", "il_L2"}
        assert full_refresh_by_id["il_L2"]["subscription"] == incremental_by_id["il_L2"]["subscription"] == "sub_S"
        assert all(record["invoice_id"] == "in_L" for record in full_refresh_records + incremental_records)

    @HttpMocker()
    def test_mixed_truncated_and_embedded_legacy_events_emit_only_il_ids(self, http_mocker: HttpMocker) -> None:
        period_start = int(_STATE_DATE.timestamp())
        embedded_m1 = [
            {
                "id": f"ii_M1_{index}",
                "unique_id": f"il_M1_{index}",
                "object": "line_item",
                "amount": 100 + index,
                "currency": "usd",
                "type": "invoiceitem",
                "livemode": False,
                "period": {"start": period_start, "end": period_start + 3600},
                "subscription": "sub_S",
            }
            for index in range(10)
        ]
        modern_m1 = [
            {
                "id": f"il_M1_{index}",
                "object": "line_item",
                "amount": 100 + index,
                "currency": "usd",
                "type": "invoiceitem",
                "livemode": False,
                "period": {"start": period_start, "end": period_start + 3600},
                "subscription": "sub_S",
                "invoice": "in_M1",
            }
            for index in range(12)
        ]
        embedded_m2 = [
            {
                "id": "ii_M2_0",
                "unique_id": "il_M2_0",
                "object": "line_item",
                "amount": 100,
                "currency": "usd",
                "type": "invoiceitem",
                "livemode": False,
                "period": {"start": period_start, "end": period_start + 3600},
                "subscription": "sub_S",
            },
            {
                "id": "sub_S",
                "unique_id": "il_M2_1",
                "unique_line_item_id": "sli_M2_1",
                "object": "line_item",
                "amount": 200,
                "currency": "usd",
                "type": "subscription",
                "livemode": False,
                "period": {"start": period_start, "end": period_start + 3600},
                "subscription": None,
            },
        ]
        events_request = _events_request().with_any_query_params().build()
        http_mocker.get(
            events_request,
            _raw_list_response(
                [
                    _legacy_invoice_event("invoice.updated", "2018-02-28", "in_M1", 1, embedded_m1, has_more=True, total_count=12),
                    _legacy_invoice_event("invoice.updated", "2018-02-28", "in_M2", 2, embedded_m2),
                ]
            ),
        )
        lines_request = _raw_invoice_lines_request("in_M1").build()
        http_mocker.get(lines_request, _raw_list_response(modern_m1))

        output = _read_incremental(http_mocker)
        records = [record.record.data for record in output.records]
        records_by_id = {record["id"]: record for record in records}
        expected_ids = {*(f"il_M1_{index}" for index in range(12)), "il_M2_0", "il_M2_1"}

        assert all(record["id"].startswith("il_") for record in records)
        assert len(records) == 14
        assert len(records_by_id) == 14
        assert set(records_by_id) == expected_ids
        assert all(records_by_id[f"il_M1_{index}"]["invoice_id"] == "in_M1" for index in range(12))
        assert records_by_id["il_M2_0"]["invoice_id"] == records_by_id["il_M2_1"]["invoice_id"] == "in_M2"
        assert records_by_id["il_M2_1"].get("subscription") == "sub_S"
        assert all(not {"unique_id", "unique_line_item_id", "original_record"} & record.keys() for record in records)
