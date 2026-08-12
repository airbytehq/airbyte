# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from urllib.parse import urlencode

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_URL = "https://public-api.granola.ai/v1/notes"
_CONFIG = {"api_key": "test-api-key", "start_date": "2025-10-12"}


def _request_url(created_after: str, created_before: str) -> str:
    query = urlencode(
        [
            ("page_size", "30"),
            ("created_after", created_after),
            ("created_before", created_before),
        ]
    )
    return f"{_BASE_URL}?{query}"


def _request(created_after: str, created_before: str) -> HttpRequest:
    return HttpRequest(_request_url(created_after, created_before))


def _read_notes(config: dict, state=None):
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream("notes", SyncMode.incremental).build()
    return read(source, config=config, catalog=catalog, state=state)


@freezegun.freeze_time("2025-12-12T00:00:00Z")
def test_incremental_requests_cover_each_partition():
    bounds = [
        ("2025-10-12T00:00:00Z", "2025-11-10T23:59:59Z"),
        ("2025-11-11T00:00:00Z", "2025-12-10T23:59:59Z"),
        ("2025-12-11T00:00:00Z", "2025-12-12T00:00:00Z"),
    ]
    with HttpMocker() as http_mocker:
        for created_after, created_before in bounds:
            http_mocker.get(
                _request(created_after, created_before),
                HttpResponse(body=json.dumps({"notes": [], "cursor": "", "hasMore": False}), status_code=200),
            )

        output = _read_notes(_CONFIG)

    assert output.records == []


@freezegun.freeze_time("2025-12-12T00:00:00Z")
def test_boundary_date_record_is_emitted():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("2025-10-12T00:00:00Z", "2025-11-10T23:59:59Z"),
            HttpResponse(
                body=json.dumps(
                    {
                        "notes": [{"id": "boundary-note", "created_at": "2025-11-10T12:00:00Z"}],
                        "cursor": "",
                        "hasMore": False,
                    }
                ),
                status_code=200,
            ),
        )
        for created_after, created_before in [
            ("2025-11-11T00:00:00Z", "2025-12-10T23:59:59Z"),
            ("2025-12-11T00:00:00Z", "2025-12-12T00:00:00Z"),
        ]:
            http_mocker.get(
                _request(created_after, created_before),
                HttpResponse(body=json.dumps({"notes": [], "cursor": "", "hasMore": False}), status_code=200),
            )

        output = _read_notes(_CONFIG)

    assert [record.record.data["id"] for record in output.records] == ["boundary-note"]


@freezegun.freeze_time("2025-12-12T00:00:00Z")
def test_legacy_date_only_state_is_parsed_and_reformatted():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("2025-11-10T00:00:00Z", "2025-12-09T23:59:59Z"),
            HttpResponse(
                body=json.dumps(
                    {
                        "notes": [{"id": "new-note", "created_at": "2025-11-11T00:00:00Z"}],
                        "cursor": "",
                        "hasMore": False,
                    }
                ),
                status_code=200,
            ),
        )
        http_mocker.get(
            _request("2025-12-10T00:00:00Z", "2025-12-12T00:00:00Z"),
            HttpResponse(body=json.dumps({"notes": [], "cursor": "", "hasMore": False}), status_code=200),
        )
        state = StateBuilder().with_stream_state("notes", {"created_at": "2025-11-10"}).build()

        output = _read_notes({"api_key": "test-api-key"}, state=state)

    assert [record.record.data["id"] for record in output.records] == ["new-note"]
    assert output.state_messages
    state_value = output.state_messages[-1].state.stream.stream_state.created_at
    assert state_value.endswith("T00:00:00Z")
    assert state_value == "2025-11-11T00:00:00Z"
