# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest import TestCase

from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.shopify_graphql.bulk.query import ShopifyBulkTemplates, Transaction
from source_shopify.streams.base_streams import ShopifyStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.integration.api.authentication import grant_all_scopes, set_up_shop
from unit_tests.integration.api.bulk import JobCreationResponseBuilder, JobStatusResponseBuilder, create_job_status_request


_SHOP_NAME = "airbyte-integration-test"
_STREAM = "transactions"
_BULK_OPERATION_ID = "gid://shopify/BulkOperation/4472588009661"
_URL_GRAPHQL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}/graphql.json"
_JOB_RESULT_URL = (
    "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/transactions-final"
    "?response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693950.jsonl%22&response-content-type=application%2Fjsonl"
)

# the saved `created_at` state and the sync time, taken from the reported sync (17:01 Paris time)
_STATE_VALUE = "2026-10-22T14:16:17+00:00"
_SYNC_TIME = "2026-10-22T15:01:00+00:00"


def _config() -> Dict[str, Any]:
    return {
        "start_date": "2026-01-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "bulk_window_in_days": 30,
    }


def _job_creation_request(start: str, end: str) -> HttpRequest:
    query = Transaction(_config()).get("updated_at", start, end)
    return HttpRequest(url=_URL_GRAPHQL, body=json.dumps({"query": ShopifyBulkTemplates.prepare(query)}))


def _order_line(
    order_id: int,
    order_created_at: str,
    order_updated_at: str,
    transaction_id: int,
    transaction_created_at: str,
    kind: str,
    status: str,
) -> str:
    return json.dumps(
        {
            "__typename": "Order",
            "id": f"gid://shopify/Order/{order_id}",
            "currency": "EUR",
            "order_created_at": order_created_at,
            "order_updated_at": order_updated_at,
            "transactions": [
                {
                    "id": f"gid://shopify/OrderTransaction/{transaction_id}",
                    "errorCode": None,
                    "test": False,
                    "kind": kind,
                    "amount": "57.23",
                    "createdAt": transaction_created_at,
                    "status": status,
                    "processedAt": transaction_created_at,
                    "gateway": "shopify_payments",
                    "paymentId": f"r{transaction_id}",
                    "accountNumber": None,
                    "formattedGateway": "Shopify Payments",
                    "manuallyCapturable": False,
                    "receipt": "{}",
                    "parentTransaction": None,
                    "authorization": None,
                    "totalUnsettledSet": {
                        "presentmentMoney": {"amount": "0.0", "currency": "EUR"},
                        "shopMoney": {"amount": "0.0", "currency": "EUR"},
                    },
                    "amountSet": {"shop_money": {"amount": "57.23", "currency": "EUR"}},
                    "fees": [],
                    "paymentDetails": {},
                }
            ],
        }
    )


@freeze_time(datetime.fromisoformat(_SYNC_TIME))
class TransactionsIncrementalTest(TestCase):
    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()
        set_up_shop(self._http_mocker, _SHOP_NAME)
        grant_all_scopes(self._http_mocker, _SHOP_NAME)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def _mock_bulk_job(self, start: str, end: str, lines: List[str]) -> None:
        self._http_mocker.post(
            _job_creation_request(start, end),
            JobCreationResponseBuilder(job_created_at="2026-10-22T15:00:00Z").with_bulk_operation_id(_BULK_OPERATION_ID).build(),
        )
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        self._http_mocker.get(HttpRequest(_JOB_RESULT_URL), HttpResponse("\n".join(lines) + "\n", status_code=200))

    def _read(self, state: Optional[Dict[str, Any]]) -> EntrypointOutput:
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
        return read(SourceShopify(), _config(), catalog, StateBuilder().with_stream_state(_STREAM, state).build())

    def test_transaction_updated_on_order_updated_after_state_is_emitted(self) -> None:
        """
        A refund created before the saved `created_at` state changes from PENDING to SUCCESS later on.
        Its order is updated after the saved state, so the bulk job returns it again,
        and the updated transaction is expected to be emitted, even though its `created_at` predates the state.
        """
        self._mock_bulk_job(
            _STATE_VALUE,
            _SYNC_TIME,
            [
                # refund created before the state, its order was updated after the state (status became SUCCESS) -> emitted
                _order_line(1, "2026-10-20T09:00:00Z", "2026-10-22T14:55:00Z", 1001, "2026-10-21T10:00:00Z", "REFUND", "SUCCESS"),
                # a new transaction, created after the state -> emitted
                _order_line(2, "2026-10-22T14:30:00Z", "2026-10-22T14:30:05Z", 1002, "2026-10-22T14:30:00Z", "SALE", "SUCCESS"),
                # both the order and the transaction predate the state (order last updated before the state) -> not emitted
                _order_line(3, "2026-10-20T09:00:00Z", "2026-10-22T14:00:00Z", 1003, "2026-10-21T10:00:00Z", "REFUND", "PENDING"),
            ],
        )

        output = self._read({"created_at": _STATE_VALUE})

        assert output.errors == []
        records = {record.record.data["id"]: record.record.data for record in output.records}
        assert sorted(records) == [1001, 1002]
        assert records[1001]["status"] == "SUCCESS"
        # parent order fields used for the state comparison are not part of the output
        assert all("order_created_at" not in data and "order_updated_at" not in data for data in records.values())
        # the state does not move backwards when an older transaction is re-emitted
        assert output.most_recent_state.stream_state.created_at == "2026-10-22T14:30:00+00:00"
