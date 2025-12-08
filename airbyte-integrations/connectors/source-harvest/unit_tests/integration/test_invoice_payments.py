# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_resource_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "invoice_payments"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestInvoicePaymentsStream(TestCase):
    """Tests for the Harvest 'invoice_payments' stream."""

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test that connector correctly fetches invoice_payments.

        Note: invoice_payments is a substream of invoices, so we need to mock both.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock the parent invoices stream with 2 invoices
        with open(get_resource_path("http/response/invoices.json")) as f:
            invoices_data = json.load(f)

        # Add a second invoice to test multi-parent retrieval
        invoice_2 = invoices_data["invoices"][0].copy()
        invoice_2["id"] = 2
        invoice_2["number"] = "INV-002"
        invoices_data["invoices"].append(invoice_2)
        invoices_data["total_entries"] = 2

        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(invoices_data), status_code=200),
        )

        # Mock the invoice_payments substream for first invoice
        with open(get_resource_path("http/response/invoice_payments.json")) as f:
            response_data_1 = json.load(f)

        # The path will be /invoices/{invoice_id}/payments
        from airbyte_cdk.test.mock_http import HttpRequest

        invoice_id_1 = invoices_data["invoices"][0]["id"]
        http_mocker.get(
            HttpRequest(
                url=f"https://api.harvestapp.com/v2/invoices/{invoice_id_1}/payments",
                query_params={"per_page": "50", "updated_since": "2021-01-01T00:00:00Z"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(body=json.dumps(response_data_1), status_code=200),
        )

        # Mock the invoice_payments substream for second invoice
        response_data_2 = response_data_1.copy()
        if "invoice_payments" in response_data_2 and len(response_data_2["invoice_payments"]) > 0:
            payment_2 = response_data_2["invoice_payments"][0].copy()
            payment_2["id"] = payment_2.get("id", 0) + 1000
            response_data_2["invoice_payments"] = [payment_2]

        invoice_id_2 = invoices_data["invoices"][1]["id"]
        http_mocker.get(
            HttpRequest(
                url=f"https://api.harvestapp.com/v2/invoices/{invoice_id_2}/payments",
                query_params={"per_page": "50", "updated_since": "2021-01-01T00:00:00Z"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(body=json.dumps(response_data_2), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve payments from both invoices
        assert len(output.records) >= 2
        assert output.records[0].record.stream == _STREAM_NAME

        # ASSERT: Transformation should add parent_id field to records
        for record in output.records:
            assert "parent_id" in record.record.data, "Transformation should add 'parent_id' field to record"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        """
        Test handling of empty results when an invoice has no payments.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock the parent invoices stream
        parent_invoice = {
            "id": 1,
            "client_id": 123,
            "number": "INV-001",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {"invoices": [parent_invoice], "per_page": 50, "total_pages": 1, "total_entries": 1, "page": 1, "links": {}}
                ),
                status_code=200,
            ),
        )

        # Mock empty invoice_payments substream response
        from airbyte_cdk.test.mock_http import HttpRequest

        http_mocker.get(
            HttpRequest(
                url="https://api.harvestapp.com/v2/invoices/1/payments",
                query_params={"per_page": "50", "updated_since": "2021-01-01T00:00:00Z"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(
                body=json.dumps({"invoice_payments": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: No records but no errors
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 401 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").build()

        # Mock parent invoices stream with auth error
        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint(_ACCOUNT_ID, "invalid_token")
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps({"error": "invalid_token"}), status_code=401),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_forbidden_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 403 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock parent invoices stream with auth error
        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps({"error": "forbidden"}), status_code=403),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_not_found_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 404 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock parent invoices stream with not found error
        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps({"error": "not_found"}), status_code=404),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with state."""
        config = (
            ConfigBuilder()
            .with_account_id(_ACCOUNT_ID)
            .with_api_token(_API_TOKEN)
            .with_replication_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc))
            .build()
        )
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": "2024-01-01T00:00:00Z"}).build()

        # Mock parent invoices stream
        parent_invoice = {
            "id": 1,
            "client_id": 1,
            "number": "INV-001",
            "amount": 10000.0,
            "state": "open",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2024-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {"invoices": [parent_invoice], "per_page": 50, "total_pages": 1, "total_entries": 1, "page": 1, "links": {}}
                ),
                status_code=200,
            ),
        )

        # Mock invoice_payments substream
        from airbyte_cdk.test.mock_http import HttpRequest

        http_mocker.get(
            HttpRequest(
                url="https://api.harvestapp.com/v2/invoices/1/payments",
                query_params={"per_page": "50", "updated_since": "2024-01-01T00:00:00Z"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "invoice_payments": [{"id": 9001, "created_at": "2024-01-02T10:00:00Z", "updated_at": "2024-01-02T10:00:00Z"}],
                        "per_page": 50,
                        "total_pages": 1,
                        "page": 1,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 9001
        assert output.records[0].record.data["updated_at"] == "2024-01-02T10:00:00Z"
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert latest_state.__dict__["state"]["updated_at"] == "2024-01-02T10:00:00Z"
