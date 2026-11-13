# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
`transaction` is a POST stream: credentials, the `start_date`/`end_date` cursor window
and the `options.offset` pagination token all travel in the JSON body. Pagination
advances the offset by the number of records on the previous page and stops on an
empty page.
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import BASE_URL, ConfigBuilder, credentials_body


_NOW = "2026-01-15T12:00:00Z"
_STREAM_NAME = "transaction"


def _transactions_request(start_date: str, end_date: str, offset: Optional[int] = None) -> HttpRequest:
    options: Dict[str, Any] = {} if offset is None else {"offset": offset}
    body = {**credentials_body(), "options": options, "start_date": start_date, "end_date": end_date}
    return HttpRequest(url=f"{BASE_URL}/transactions/get", body=body)


def _transactions_response(transactions: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"transactions": transactions}), status_code=200)


def _transaction(transaction_id: str, date: str) -> Dict[str, Any]:
    return {"transaction_id": transaction_id, "account_id": "acc-1", "amount": 12.5, "date": date, "name": "Coffee"}


def _read(state: Optional[List[AirbyteStateMessage]] = None) -> EntrypointOutput:
    config = ConfigBuilder().with_start_date("2026-01-01").build()
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


@freezegun.freeze_time(_NOW)
class TestTransaction(TestCase):
    @HttpMocker()
    def test_first_sync_paginates_by_offset_and_emits_latest_date_as_state(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            _transactions_request("2026-01-01", "2026-01-15"),
            _transactions_response([_transaction("t1", "2026-01-02"), _transaction("t2", "2026-01-05")]),
        )
        http_mocker.post(
            _transactions_request("2026-01-01", "2026-01-15", offset=2),
            _transactions_response([_transaction("t3", "2026-01-10")]),
        )
        http_mocker.post(_transactions_request("2026-01-01", "2026-01-15", offset=3), _transactions_response([]))

        output = _read()

        assert [record.record.data["transaction_id"] for record in output.records] == ["t1", "t2", "t3"]
        assert output.most_recent_state.stream_state.__dict__ == {"date": "2026-01-10"}

    @HttpMocker()
    def test_sync_with_state_starts_window_at_state_date(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            _transactions_request("2026-01-10", "2026-01-15"),
            _transactions_response([_transaction("t3", "2026-01-10"), _transaction("t4", "2026-01-12")]),
        )
        http_mocker.post(_transactions_request("2026-01-10", "2026-01-15", offset=2), _transactions_response([]))

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"date": "2026-01-10"}).build()
        output = _read(state=state)

        # The cursor window is inclusive, so the transaction dated on the state value is re-emitted.
        assert [record.record.data["transaction_id"] for record in output.records] == ["t3", "t4"]
        assert output.most_recent_state.stream_state.__dict__ == {"date": "2026-01-12"}
