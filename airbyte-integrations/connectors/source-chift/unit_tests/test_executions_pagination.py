# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards for the `executions` stream's pagination and for `start_date` staying optional.

The pagination test reproduces the defect `/ai-prove-fix` found on this PR: with
`start_from_page: 0` the first request omits `page`, the API serves page 1, and the second
request then asks for `page=1` — the same page again. A 120-execution sync emitted 170 records.
"""

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_BASE = "https://api.chift.eu"
_SYNC_ID = "sync-1"
_PAGE_SIZE = 50
_START_DATE = "2026-07-01T00:00:00"
_CONFIG = {
    "client_id": "test-client-id",
    "account_id": "test-account-id",
    "client_secret": "test-client-secret",
    "start_date": _START_DATE,
}


def _execution(index: int) -> dict:
    return {
        "id": f"exec-{index:04d}",
        "start": f"2026-07-02T00:00:{index % 60:02d}.000000",
        "end": None,
        "status": "success",
        "flow_id": "flow-1",
        "consumer_id": "consumer-1",
        "parentexecutionid": None,
    }


def _items(records: list) -> HttpResponse:
    """Chift wraps list responses in an `items` envelope."""
    return HttpResponse(body=json.dumps({"items": records, "total": len(records)}))


def _executions_request(page: int = None, date_from: str = _START_DATE) -> HttpRequest:
    """`page` is omitted on the first request: with `start_from_page: 1` the API's own default
    serves page 1, and the paginator only starts injecting `page` from the second request."""
    params = {"size": str(_PAGE_SIZE), "date_from": date_from}
    if page is not None:
        params["page"] = str(page)
    return HttpRequest(url=f"{_BASE}/syncs/{_SYNC_ID}/executions", query_params=params)


def _mock_auth_and_parent(http_mocker: HttpMocker) -> None:
    # The matcher compares request bodies, so the login body has to be spelled out. It also
    # documents the shape the `| tojson` interpolation produces: three JSON strings.
    http_mocker.post(
        HttpRequest(
            url=f"{_BASE}/token",
            body={
                "clientId": _CONFIG["client_id"],
                "accountId": _CONFIG["account_id"],
                "clientSecret": _CONFIG["client_secret"],
            },
        ),
        HttpResponse(body=json.dumps({"access_token": "test-token"})),
    )
    # `syncs` extracts with `field_path: []`, so its response is a bare array, not an envelope.
    http_mocker.get(
        HttpRequest(url=f"{_BASE}/syncs"),
        HttpResponse(body=json.dumps([{"syncid": _SYNC_ID, "name": "Sync 1"}])),
    )


def _read(config: dict, sync_mode: SyncMode = SyncMode.full_refresh):
    return read(
        get_source(config),
        config=config,
        catalog=CatalogBuilder().with_stream("executions", sync_mode).build(),
    )


class TestExecutionsPagination(TestCase):
    @HttpMocker()
    def test_pagination_starts_at_page_one_and_emits_no_duplicates(self, http_mocker: HttpMocker):
        """With `start_from_page: 0` the first page is fetched twice; 120 executions became 170 records."""
        _mock_auth_and_parent(http_mocker)
        http_mocker.get(_executions_request(), _items([_execution(i) for i in range(0, 50)]))
        http_mocker.get(_executions_request(2), _items([_execution(i) for i in range(50, 100)]))
        http_mocker.get(_executions_request(3), _items([_execution(i) for i in range(100, 120)]))

        output = _read(_CONFIG)

        ids = [record.record.data["id"] for record in output.records]
        assert len(ids) == 120, f"expected 120 records, got {len(ids)}"
        assert len(set(ids)) == 120, f"expected no duplicates, got {len(ids) - len(set(ids))}"

    @HttpMocker()
    def test_cursor_accepts_rfc3339_utc_timestamps(self, http_mocker: HttpMocker):
        """Chift only promises `format: date-time` (RFC 3339) for `start`. Without the `%z`
        fallback formats a Z-suffixed value is skipped by the cursor ("Skipping cursor update")
        and state never advances, silently degrading incremental to a rolling full re-read."""
        _mock_auth_and_parent(http_mocker)
        record = _execution(1)
        record["start"] = "2026-07-15T10:00:00Z"
        http_mocker.get(_executions_request(), _items([record]))

        output = _read(_CONFIG, sync_mode=SyncMode.incremental)

        assert len(output.records) == 1
        assert output.errors == []
        partition_states = getattr(output.state_messages[-1].state.stream.stream_state, "states", [])
        assert partition_states and partition_states[0]["cursor"] == {
            "start": "2026-07-15T10:00:00"
        }, f"cursor did not observe the Z-suffixed value; state: {partition_states}"

    @HttpMocker()
    def test_sync_runs_without_start_date(self, http_mocker: HttpMocker):
        """`start_date` is optional, so an existing config that predates it must keep working."""
        config = {key: value for key, value in _CONFIG.items() if key != "start_date"}
        _mock_auth_and_parent(http_mocker)
        http_mocker.get(
            _executions_request(date_from="1970-01-01T00:00:00"),
            _items([_execution(1)]),
        )

        output = _read(config)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "exec-0001"
