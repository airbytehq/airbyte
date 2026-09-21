# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
HttpMocker tests for source-quickbooks manifest.yaml.

Each of the 28 streams is read against a mocked Intuit Accounting API: the query
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
    "bill_payments": "BillPayment",
    "bills": "Bill",
    "budgets": "Budget",
    "classes": "Class",
    "credit_memos": "CreditMemo",
    "customers": "Customer",
    "departments": "Department",
    "deposits": "Deposit",
    "employees": "Employee",
    "estimates": "Estimate",
    "invoices": "Invoice",
    "items": "Item",
    "journal_entries": "JournalEntry",
    "payment_methods": "PaymentMethod",
    "payments": "Payment",
    "purchase_orders": "PurchaseOrder",
    "purchases": "Purchase",
    "refund_receipts": "RefundReceipt",
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
    assert record.data["airbyte_cursor"]

    statuses = [
        message.trace.stream_status.status
        for message in output._messages
        if message.type == Type.TRACE and message.trace.type == TraceType.STREAM_STATUS
    ]
    assert AirbyteStreamStatus.COMPLETE in statuses
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
