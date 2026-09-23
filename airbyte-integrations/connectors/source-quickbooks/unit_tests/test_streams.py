# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
HttpMocker tests for source-quickbooks manifest.yaml.

Each of the 34 streams is read against a mocked Intuit Accounting API: the query
endpoint returns a single entity record, and the OAuth token endpoint returns a
rotated token in case the authenticator refreshes. One extra test feeds the
legacy pre-4.0.0 nested config shape to prove the manifest's config migration
makes it readable end to end.
"""

import datetime
import json
from pathlib import Path

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk.models import (
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
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

FULL_REFRESH_STREAMS = {"company_info", "preferences"}


def _flat_config() -> dict:
    return {
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
        "realm_id": REALM_ID,
        "start_date": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sandbox": True,
        "access_token": "test-access-token",
        "token_expiry_date": "2124-01-01T00:00:00Z",
    }


def _nested_config() -> dict:
    flat = _flat_config()
    return {
        "sandbox": flat["sandbox"],
        "start_date": flat["start_date"],
        "credentials": flat,
    }


def _catalog(stream_name: str) -> ConfiguredAirbyteCatalog:
    if stream_name in FULL_REFRESH_STREAMS:
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


def _source(config: dict, manifest: dict) -> ConcurrentDeclarativeSource:
    return ConcurrentDeclarativeSource(
        source_config=manifest,
        config=config,
        catalog=None,
        state=None,
    )


def _mock_intuit(http_mocker: HttpMocker, entity: str) -> None:
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
        HttpRequest(QUERY_URL, query_params="any query_parameters"),
        [record_page] + [empty_page] * 10,
    )


@pytest.mark.parametrize("stream_name,entity", STREAM_ENTITY.items())
def test_stream_reads_single_record(stream_name: str, entity: str, manifest):
    config = _flat_config()
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


def test_nested_legacy_config_is_migrated_and_read(manifest):
    """Pre-4.0.0 `credentials.*` configs are flattened by the manifest migration before spec validation."""
    config = _nested_config()
    with HttpMocker() as http_mocker:
        _mock_intuit(http_mocker, "Account")

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
    config = _flat_config()
    config["start_date"] = "2026-03-14T00:00:00Z"
    config.update(overrides)
    return config


def _incremental_query(entity: str, start_position: int, max_results: int = 200) -> str:
    return (
        f"SELECT * FROM {entity} "
        f"WHERE Metadata.LastUpdatedTime > '{WINDOW_START}' "
        f"AND Metadata.LastUpdatedTime <= '{WINDOW_END}' "
        "AND Active IN (true, false) "
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
def test_incremental_stream_paginates_with_explicit_queries(manifest):
    """5 + 5 + 2 records over three pages: STARTPOSITION advances by the page size and the read stops on the short page."""
    config = _frozen_config()
    first = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 1)})
    second = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 6)})
    third = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 11)})

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
def test_max_results_is_configurable(manifest):
    config = _frozen_config(max_results=1000)
    request = HttpRequest(QUERY_URL, query_params={"query": _incremental_query("Account", 1, max_results=1000)})

    with HttpMocker() as http_mocker:
        http_mocker.get(request, _page("Account", 1, 2))

        output = read(_source(config, manifest), config=config, catalog=_catalog("accounts"), state=None)

        http_mocker.assert_number_of_calls(request, 1)

    assert len(output.records) == 2


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
        "STARTPOSITION 1 MAXRESULTS 200"
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
            f"&client_id={config['client_id']}"
            f"&client_secret={config['client_secret']}"
            f"&refresh_token={config['refresh_token']}"
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
    assert emitted["refresh_token"] == "rotated-refresh-token"
    assert emitted["access_token"] == "rotated-access-token"
