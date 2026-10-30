# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
HttpMocker tests for source-quickbooks manifest.yaml.

Each of the 34 streams is read against a mocked Intuit Accounting API: the query
endpoint returns a single entity record, and the OAuth token endpoint returns a
rotated token in case the authenticator refreshes. Authentication fields are
supplied under `credentials`, with tests for sandbox and production routing.
"""

import datetime
import json
from pathlib import Path

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    FailureType,
    Status,
    StreamDescriptor,
    SyncMode,
    TraceType,
    Type,
)
from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
    ConcurrentDeclarativeSource,
)
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

REALM_ID = "4620816365288779920"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
QUERY_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{REALM_ID}/query"
PRODUCTION_QUERY_URL = f"https://quickbooks.api.intuit.com/v3/company/{REALM_ID}/query"

STREAM_ENTITY = {
    "accounts": "Account",
    "attachables": "Attachable",
    "bill_payments": "BillPayment",
    "bills": "Bill",
    "budgets": "Budget",
    "classes": "Class",
    "company_info": "CompanyInfo",
    "credit_card_payments": "CreditCardPaymentTxn",
    "credit_memos": "CreditMemo",
    "customers": "Customer",
    "departments": "Department",
    "deposits": "Deposit",
    "employees": "Employee",
    "estimates": "Estimate",
    "exchange_rates": "ExchangeRate",
    "invoices": "Invoice",
    "items": "Item",
    "journal_entries": "JournalEntry",
    "payment_methods": "PaymentMethod",
    "payments": "Payment",
    "preferences": "Preferences",
    "purchase_orders": "PurchaseOrder",
    "purchases": "Purchase",
    "refund_receipts": "RefundReceipt",
    "reimburse_charges": "ReimburseCharge",
    "sales_receipts": "SalesReceipt",
    "tax_agencies": "TaxAgency",
    "tax_codes": "TaxCode",
    "tax_rates": "TaxRate",
    "terms": "Term",
    "time_activities": "TimeActivity",
    "transfers": "Transfer",
    "vendor_credits": "VendorCredit",
    "vendors": "Vendor",
}

REFERENCE_STREAMS = {
    "accounts": "Account",
    "classes": "Class",
    "departments": "Department",
    "employees": "Employee",
    "payment_methods": "PaymentMethod",
    "tax_agencies": "TaxAgency",
    "tax_codes": "TaxCode",
    "tax_rates": "TaxRate",
    "terms": "Term",
}

FULL_REFRESH_STREAMS = {"company_info", "preferences"}

ACTIVE_LESS_STREAMS = {
    "attachables",
    "bill_payments",
    "bills",
    "credit_card_payments",
    "credit_memos",
    "deposits",
    "estimates",
    "exchange_rates",
    "invoices",
    "journal_entries",
    "payments",
    "purchase_orders",
    "purchases",
    "refund_receipts",
    "reimburse_charges",
    "sales_receipts",
    "tax_agencies",
    "time_activities",
    "transfers",
    "vendor_credits",
}

WINDOWED_STREAMS = {
    stream_name: entity
    for stream_name, entity in STREAM_ENTITY.items()
    if stream_name not in REFERENCE_STREAMS and stream_name not in FULL_REFRESH_STREAMS
}


def _credentials_config(auth_type: str = "client_credentials", sandbox: bool = True) -> dict:
    return {
        "start_date": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "credentials": {
            "auth_type": auth_type,
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token",
            "realm_id": REALM_ID,
            "sandbox": sandbox,
            "access_token": "test-access-token",
            "token_expiry_date": "2124-01-01T00:00:00Z",
        },
    }


def _catalog(stream_name: str, sync_mode: SyncMode | None = None) -> ConfiguredAirbyteCatalog:
    if sync_mode is None:
        sync_mode = SyncMode.full_refresh if stream_name in FULL_REFRESH_STREAMS else SyncMode.incremental

    if sync_mode == SyncMode.full_refresh:
        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name=stream_name,
                        json_schema={},
                        supported_sync_modes=[SyncMode.full_refresh],
                    ),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
            ]
        )
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={},
                    supported_sync_modes=[SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
                cursor_field=["airbyte_cursor"],
            )
        ]
    )


@pytest.fixture(scope="module")
def manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _source(
    config: dict,
    manifest: dict,
    state: list[AirbyteStateMessage] | None = None,
) -> ConcurrentDeclarativeSource:
    return ConcurrentDeclarativeSource(
        source_config=manifest,
        config=config,
        catalog=None,
        state=state,
    )


def _state(stream_name: str, cursor: str) -> list[AirbyteStateMessage]:
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream_name),
                stream_state=AirbyteStateBlob(airbyte_cursor=cursor),
            ),
        )
    ]


def _mock_intuit(http_mocker: HttpMocker, entity: str, query_url: str = QUERY_URL) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    create_time = (now - datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S-08:00")
    update_time = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S-08:00")
    time_hdr = now.strftime("%Y-%m-%dT%H:%M:%S.000-08:00")
    http_mocker.post(
        HttpRequest(TOKEN_URL),
        HttpResponse(
            body=json.dumps(
                {
                    "access_token": "rotated-access-token",
                    "refresh_token": "rotated-refresh-token",
                    "expires_in": 3600,
                    "x_refresh_token_expires_in": 8726400,
                    "token_type": "bearer",
                }
            ),
            status_code=200,
        ),
    )
    record_page = HttpResponse(
        body=json.dumps(
            {
                "QueryResponse": {
                    entity: [
                        {
                            "Id": "1",
                            "MetaData": {
                                "CreateTime": create_time,
                                "LastUpdatedTime": update_time,
                            },
                        }
                    ],
                    "startPosition": 1,
                    "maxResults": 1,
                },
                "time": time_hdr,
            }
        ),
        status_code=200,
    )
    empty_page = HttpResponse(
        body=json.dumps({"QueryResponse": {}, "time": time_hdr}),
        status_code=200,
    )
    # First 30-day slice returns the record; any later slices get empty pages.
    http_mocker.get(
        HttpRequest(query_url, query_params="any query_parameters"),
        [record_page] + [empty_page] * 10,
    )


@pytest.mark.parametrize("stream_name,entity", STREAM_ENTITY.items())
def test_stream_reads_single_record(stream_name: str, entity: str, manifest):
    config = _credentials_config()
    with HttpMocker() as http_mocker:
        _mock_intuit(http_mocker, entity)

        output = read(
            _source(config, manifest),
            config=config,
            catalog=_catalog(stream_name),
            state=None,
        )

    assert output.errors == []
    assert len(output.records) == 1
    record = output.records[0].record
    assert record.stream == stream_name
    assert record.data["Id"] == "1"
    if stream_name not in FULL_REFRESH_STREAMS:
        assert record.data["airbyte_cursor"]

    statuses = [
        message.trace.stream_status.status
        for message in output._messages
        if message.type == Type.TRACE and message.trace.type == TraceType.STREAM_STATUS
    ]
    assert AirbyteStreamStatus.COMPLETE in statuses
    if stream_name not in FULL_REFRESH_STREAMS:
        assert any(message.type == Type.STATE for message in output._messages)


def test_oauth_credentials_use_production_when_sandbox_is_true(manifest):
    config = _credentials_config(auth_type="oauth2.0")
    with HttpMocker() as http_mocker:
        _mock_intuit(http_mocker, "Account", query_url=PRODUCTION_QUERY_URL)

        output = read(
            _source(config, manifest),
            config=config,
            catalog=_catalog("accounts"),
            state=None,
        )

    assert output.errors == []
    assert len(output.records) == 1
    assert output.records[0].record.data["Id"] == "1"


FROZEN_NOW = "2026-03-15T12:00:00+00:00"
WINDOW_START = "2026-03-14T00:00:00+00:00"
WINDOW_END = "2026-03-15T12:00:00+00:00"


def _frozen_config(**overrides) -> dict:
    config = _credentials_config()
    config["start_date"] = "2026-03-14T00:00:00Z"
    for key, value in overrides.items():
        if key in {"start_date", "max_results"}:
            config[key] = value
        else:
            config["credentials"][key] = value
    return config


def _incremental_query(entity: str, start_position: int, max_results: int = 1000) -> str:
    return _query(entity, WINDOW_START, WINDOW_END, start_position, max_results)


def _query(
    entity: str,
    lower: str,
    upper: str,
    start_position: int = 1,
    max_results: int = 1000,
    include_active: bool = True,
) -> str:
    active_filter = "AND Active IN (true, false) " if include_active else ""
    return (
        f"SELECT * FROM {entity} "
        f"WHERE Metadata.LastUpdatedTime > '{lower}' "
        f"AND Metadata.LastUpdatedTime <= '{upper}' "
        f"{active_filter}"
        "ORDER BY Metadata.LastUpdatedTime ASC "
        f"STARTPOSITION {start_position} MAXRESULTS {max_results}"
    )


def _page(entity: str, first_id: int, count: int) -> HttpResponse:
    records = [
        {
            "Id": str(first_id + offset),
            "MetaData": {
                "CreateTime": "2026-03-14T01:00:00-08:00",
                "LastUpdatedTime": "2026-03-14T02:00:00-08:00",
            },
        }
        for offset in range(count)
    ]
    return HttpResponse(
        body=json.dumps({"QueryResponse": {entity: records}, "time": "2026-03-15T12:00:00.000-08:00"}),
        status_code=200,
    )


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize("stream_name,entity", REFERENCE_STREAMS.items())
def test_reference_streams_read_the_whole_range_in_one_window(stream_name: str, entity: str, manifest):
    config = _frozen_config(start_date="2020-01-01T00:00:00Z")
    request = HttpRequest(
        QUERY_URL,
        query_params={
            "query": _query(
                entity,
                "2020-01-01T00:00:00+00:00",
                "2026-03-15T12:00:00+00:00",
                include_active=stream_name != "tax_agencies",
            )
        },
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page(entity, 1, 3))

        output = read(
            _source(config, manifest),
            config=config,
            catalog=_catalog(stream_name),
            state=None,
        )

        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 3


@freeze_time(FROZEN_NOW)
def test_reference_stream_incremental_read_starts_from_state(manifest):
    config = _frozen_config(start_date="2020-01-01T00:00:00Z")
    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="accounts"),
                stream_state=AirbyteStateBlob(airbyte_cursor="2025-06-01T00:00:00+00:00"),
            ),
        )
    ]
    request = HttpRequest(
        QUERY_URL,
        query_params={
            "query": _query(
                "Account",
                "2025-06-01T00:00:00+00:00",
                "2026-03-15T12:00:00+00:00",
            )
        },
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page("Account", 1, 2))

        output = read(
            _source(config, manifest, state=state),
            config=config,
            catalog=_catalog("accounts"),
            state=state,
        )

        final_state = output.most_recent_state.stream_state
        final_state_data = vars(final_state)
        http_mocker.assert_number_of_calls(request, 1)

    assert set(final_state_data) == {"airbyte_cursor"}
    assert final_state_data["airbyte_cursor"] == "2026-03-14T02:00:00-0800"
    assert output.errors == []
    assert len(output.records) == 2


@freeze_time(FROZEN_NOW)
def test_transaction_streams_keep_30_day_windows(manifest):
    config = _frozen_config(start_date="2026-01-01T00:00:00Z")
    windows = [
        ("2026-01-01T00:00:00+00:00", "2026-01-31T00:00:00+00:00"),
        ("2026-01-31T00:00:00+00:00", "2026-03-02T00:00:00+00:00"),
        ("2026-03-02T00:00:00+00:00", "2026-03-15T12:00:00+00:00"),
    ]
    requests = [
        HttpRequest(
            QUERY_URL,
            query_params={"query": _query("Invoice", lower, upper, include_active=False)},
        )
        for lower, upper in windows
    ]

    with HttpMocker() as http_mocker:
        for position, request in enumerate(requests, start=1):
            http_mocker.get(request, _page("Invoice", position, 1))

        output = read(
            _source(config, manifest),
            config=config,
            catalog=_catalog("invoices"),
            state=None,
        )

        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 3


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize("stream_name,entity", WINDOWED_STREAMS.items())
def test_delegated_streams_without_state_keep_30_day_windows(stream_name: str, entity: str, manifest):
    config = _frozen_config(start_date="2026-01-01T00:00:00Z")
    windows = [
        ("2026-01-01T00:00:00+00:00", "2026-01-31T00:00:00+00:00"),
        ("2026-01-31T00:00:00+00:00", "2026-03-02T00:00:00+00:00"),
        ("2026-03-02T00:00:00+00:00", "2026-03-15T12:00:00+00:00"),
    ]
    requests = [
        HttpRequest(
            QUERY_URL,
            query_params={
                "query": _query(
                    entity,
                    lower,
                    upper,
                    include_active=stream_name not in ACTIVE_LESS_STREAMS,
                )
            },
        )
        for lower, upper in windows
    ]

    with HttpMocker() as http_mocker:
        for position, request in enumerate(requests, start=1):
            http_mocker.get(request, _page(entity, position, 1))

        output = read(
            _source(config, manifest),
            config=config,
            catalog=_catalog(stream_name),
            state=None,
        )

        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 3


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize("stream_name,entity", WINDOWED_STREAMS.items())
def test_delegated_streams_with_state_use_one_window(stream_name: str, entity: str, manifest):
    config = _frozen_config(start_date="2020-01-01T00:00:00Z")
    state = _state(stream_name, "2025-06-01T00:00:00+00:00")
    request = HttpRequest(
        QUERY_URL,
        query_params={
            "query": _query(
                entity,
                "2025-06-01T00:00:00+00:00",
                "2026-03-15T12:00:00+00:00",
                include_active=stream_name not in ACTIVE_LESS_STREAMS,
            )
        },
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page(entity, 1, 1))

        output = read(
            _source(config, manifest, state=state),
            config=config,
            catalog=_catalog(stream_name),
            state=state,
        )

        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 1


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize("stream_name,entity", [("accounts", "Account"), ("invoices", "Invoice")])
@pytest.mark.parametrize(
    "cursor,expected_cursor,start_date",
    [
        ("2025-01-01T00:00:00+00:00", "2025-01-01T00:00:00+0000", "2020-01-01T00:00:00Z"),
        ("2025-06-01T00:00:00+00:00", "2025-06-01T00:00:00+0000", "2025-06-01T00:00:00Z"),
    ],
)
def test_empty_incremental_reads_keep_the_input_cursor(
    stream_name: str, entity: str, cursor: str, expected_cursor: str, start_date: str, manifest
):
    config = _frozen_config(start_date=start_date)
    state = _state(stream_name, cursor)
    request = HttpRequest(
        QUERY_URL,
        query_params={
            "query": _query(
                entity,
                cursor,
                "2026-03-15T12:00:00+00:00",
                include_active=stream_name not in ACTIVE_LESS_STREAMS,
            )
        },
    )
    empty_page = HttpResponse(body=json.dumps({"QueryResponse": {}}), status_code=200)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, empty_page)

        output = read(
            _source(config, manifest, state=state),
            config=config,
            catalog=_catalog(stream_name),
            state=state,
        )

        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert output.records == []
    actual_cursor = output.most_recent_state.stream_state.airbyte_cursor
    assert actual_cursor == expected_cursor


@freeze_time(FROZEN_NOW)
def test_reference_stream_full_refresh_uses_one_window(manifest):
    config = _frozen_config(start_date="2020-01-01T00:00:00Z")
    request = HttpRequest(
        QUERY_URL,
        query_params={
            "query": _query(
                "Account",
                "2020-01-01T00:00:00+00:00",
                "2026-03-15T12:00:00+00:00",
            )
        },
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page("Account", 1, 1))

        output = read(
            _source(config, manifest),
            config=config,
            catalog=_catalog("accounts", SyncMode.full_refresh),
            state=None,
        )

        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 1


@freeze_time(FROZEN_NOW)
def test_delegated_stream_full_refresh_keeps_30_day_windows(manifest):
    config = _frozen_config(start_date="2026-01-01T00:00:00Z")
    windows = [
        ("2026-01-01T00:00:00+00:00", "2026-01-31T00:00:00+00:00"),
        ("2026-01-31T00:00:00+00:00", "2026-03-02T00:00:00+00:00"),
        ("2026-03-02T00:00:00+00:00", "2026-03-15T12:00:00+00:00"),
    ]
    requests = [
        HttpRequest(
            QUERY_URL,
            query_params={"query": _query("Invoice", lower, upper, include_active=False)},
        )
        for lower, upper in windows
    ]

    with HttpMocker() as http_mocker:
        for position, request in enumerate(requests, start=1):
            http_mocker.get(request, _page("Invoice", position, 1))

        output = read(
            _source(config, manifest),
            config=config,
            catalog=_catalog("invoices", SyncMode.full_refresh),
            state=None,
        )

        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 3


@pytest.mark.parametrize(
    "previous_cursor,expected_cursor",
    [("2025-06-01T00:00:00+00:00", "2025-06-01T00:00:00+0000")],
)
@freeze_time(FROZEN_NOW)
def test_delegated_stream_reports_page_two_failure_without_advancing_state(manifest, previous_cursor: str, expected_cursor: str):
    config = _frozen_config(start_date="2020-01-01T00:00:00Z", max_results=2)
    state = _state("invoices", previous_cursor)
    first = HttpRequest(
        QUERY_URL,
        query_params={
            "query": _query(
                "Invoice",
                previous_cursor,
                "2026-03-15T12:00:00+00:00",
                max_results=2,
                include_active=False,
            )
        },
    )
    second = HttpRequest(
        QUERY_URL,
        query_params={
            "query": _query(
                "Invoice",
                previous_cursor,
                "2026-03-15T12:00:00+00:00",
                start_position=3,
                max_results=2,
                include_active=False,
            )
        },
    )
    error = HttpResponse(
        body=json.dumps({"Fault": {"Error": [{"Message": "Forbidden", "code": "5010"}]}}),
        status_code=403,
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(first, _page("Invoice", 1, 2))
        http_mocker.get(second, error)

        output = read(
            _source(config, manifest, state=state),
            config=config,
            catalog=_catalog("invoices"),
            state=state,
            expecting_exception=True,
        )

        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)

    assert [record.record.data["Id"] for record in output.records] == ["1", "2"]
    assert output.errors
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    emitted_cursors = [message.state.stream.stream_state.airbyte_cursor for message in output.state_messages]
    assert emitted_cursors
    assert all(cursor == expected_cursor for cursor in emitted_cursors)


@freeze_time(FROZEN_NOW)
def test_incremental_stream_paginates_with_explicit_queries(manifest):
    """5 + 5 + 2 records at a page size of 5: STARTPOSITION advances by the page size and the read stops on the short page."""
    config = _frozen_config(max_results=5)
    first = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 1, max_results=5)})
    second = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 6, max_results=5)})
    third = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 11, max_results=5)})

    with HttpMocker() as http_mocker:
        http_mocker.get(first, _page("Account", 1, 5))
        http_mocker.get(second, _page("Account", 6, 5))
        http_mocker.get(third, _page("Account", 11, 2))

        output = read(_source(config, manifest), config=config, catalog=_catalog("accounts"), state=None)

        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)
        http_mocker.assert_number_of_calls(third, 1)

    assert output.errors == []
    assert len(output.records) == 12
    assert [record.record.data["Id"] for record in output.records] == [str(i) for i in range(1, 13)]


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize("max_results,record_count", [(None, 50), (None, 999), (300, 50), (300, 299)])
def test_window_shorter_than_page_size_makes_one_request(max_results, record_count, manifest):
    """A page with fewer records than MAXRESULTS is the last one, so no empty follow-up request is sent."""
    config = _frozen_config() if max_results is None else _frozen_config(max_results=max_results)
    request = HttpRequest(
        QUERY_URL,
        query_params={"query": _incremental_query("Account", 1, max_results=max_results or 1000)},
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page("Account", 1, record_count))

        output = read(_source(config, manifest), config=config, catalog=_catalog("accounts"), state=None)

        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == record_count


@freeze_time(FROZEN_NOW)
def test_window_that_is_an_exact_multiple_of_page_size_stops_on_the_empty_page(manifest):
    config = _frozen_config(max_results=5)
    first = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 1, max_results=5)})
    second = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 6, max_results=5)})
    third = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 11, max_results=5)})

    with HttpMocker() as http_mocker:
        http_mocker.get(first, _page("Account", 1, 5))
        http_mocker.get(second, _page("Account", 6, 5))
        http_mocker.get(third, _page("Account", 11, 0))

        output = read(_source(config, manifest), config=config, catalog=_catalog("accounts"), state=None)

        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)
        http_mocker.assert_number_of_calls(third, 1)

    assert output.errors == []
    assert len(output.records) == 10


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize("stored,expected", [(200, 1000), ("200", 1000), (300, 300), (1000, 1000)])
def test_page_size_of_200_is_migrated_to_1000(stored, expected, manifest, capsys):
    """200 was the default before 5.1.0, so a stored 200 is raised to the new default; other values are kept."""
    config = _frozen_config(max_results=stored)
    request = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 1, max_results=expected)})

    source = _source(config, manifest)
    control_lines = [line for line in capsys.readouterr().out.splitlines() if '"CONNECTOR_CONFIG"' in line]

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page("Account", 1, 2))

        output = read(source, config=config, catalog=_catalog("accounts"), state=None)

        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 2
    if stored == expected:
        assert control_lines == []
    else:
        assert len(control_lines) == 1
        assert json.loads(control_lines[0])["control"]["connectorConfig"]["config"]["max_results"] == expected


def test_page_size_defaults_to_1000(manifest):
    assert manifest["spec"]["connection_specification"]["properties"]["max_results"]["default"] == 1000


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize("stream_name,entity", [("company_info", "CompanyInfo"), ("preferences", "Preferences")])
def test_full_refresh_streams_query_without_window_or_paging(stream_name: str, entity: str, manifest):
    """Single-row entities are read with a bare `SELECT *`: no window, no `Active` clause, no MAXRESULTS."""
    config = _frozen_config()
    request = HttpRequest(QUERY_URL, query_params={"query": f"SELECT * FROM {entity}"})

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page(entity, 1, 1))

        output = read(_source(config, manifest), config=config, catalog=_catalog(stream_name), state=None)

        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 1


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize(
    "stream_name,entity",
    [("exchange_rates", "ExchangeRate"), ("attachables", "Attachable")],
)
def test_streams_without_active_field_omit_the_active_clause(stream_name: str, entity: str, manifest):
    """Intuit answers `Active IN (true, false)` with an `Invalid query` fault on these entities."""
    config = _frozen_config()
    query = (
        f"SELECT * FROM {entity} "
        f"WHERE Metadata.LastUpdatedTime > '{WINDOW_START}' "
        f"AND Metadata.LastUpdatedTime <= '{WINDOW_END}' "
        "ORDER BY Metadata.LastUpdatedTime ASC "
        "STARTPOSITION 1 MAXRESULTS 1000"
    )
    request = HttpRequest(QUERY_URL, query_params={"query": query})

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page(entity, 1, 1))

        output = read(_source(config, manifest), config=config, catalog=_catalog(stream_name), state=None)

        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors == []
    assert len(output.records) == 1


@freeze_time(FROZEN_NOW)
def test_expired_access_token_is_refreshed_and_rotation_is_persisted(manifest):
    """Intuit rotates the refresh token on every exchange; the new pair must reach the platform as a control message."""
    config = _frozen_config(access_token="stale-access-token", token_expiry_date="2020-01-01T00:00:00Z")
    token_request = HttpRequest(
        TOKEN_URL,
        body=(
            "grant_type=refresh_token"
            f"&client_id={config['credentials']['client_id']}"
            f"&client_secret={config['credentials']['client_secret']}"
            f"&refresh_token={config['credentials']['refresh_token']}"
        ),
    )
    query_request = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 1)})

    with HttpMocker() as http_mocker:
        http_mocker.post(
            token_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "access_token": "rotated-access-token",
                        "refresh_token": "rotated-refresh-token",
                        "expires_in": 3600,
                        "x_refresh_token_expires_in": 8726400,
                        "token_type": "bearer",
                    }
                ),
                status_code=200,
            ),
        )
        http_mocker.get(query_request, _page("Account", 1, 1))

        output = read(_source(config, manifest), config=config, catalog=_catalog("accounts"), state=None)

        http_mocker.assert_number_of_calls(token_request, 1)

    assert output.errors == []
    assert len(output.records) == 1

    controls = [message.control for message in output._messages if message.type == Type.CONTROL]
    assert controls, "the rotated refresh token was not emitted as a CONNECTOR_CONFIG control message"
    emitted = controls[-1].connectorConfig.config
    assert emitted["credentials"]["refresh_token"] == "rotated-refresh-token"
    assert emitted["credentials"]["access_token"] == "rotated-access-token"
