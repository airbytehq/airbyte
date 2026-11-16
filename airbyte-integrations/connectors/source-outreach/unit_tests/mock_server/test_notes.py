# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Iterator
from dataclasses import dataclass
from urllib.parse import urlencode

import pytest
from jsonschema import validate

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from unit_tests.conftest import build_source

from .config import ConfigBuilder
from .request_builder import BASE_URL
from .response_builder import error_response, page_response, resource
from .utils import given_token, read_stream, record_ids


# /prospectNotes and /accountNotes have no updatedAt: `sort=updatedAt` returns 400
# `sort_parameter.unsupported_attribute` and `filter[updatedAt]` returns 400 `filter_parameter.unknown_filter`.
# Both streams are full refresh and send neither.
_QUERY = {"count": "false", "page[size]": "1000", "newFilterSyntax": "true"}


@dataclass(frozen=True)
class NoteCase:
    name: str
    path: str
    resource_type: str
    parent: str
    scope: str

    def request(self) -> HttpRequest:
        return HttpRequest(f"{BASE_URL}{self.path}", query_params=_QUERY)

    def next_page_url(self, page_after: str) -> str:
        return f"{BASE_URL}{self.path}?{urlencode({**_QUERY, 'page[after]': page_after})}"

    def record(self, resource_id: int = 1) -> dict:
        return resource(
            resource_id,
            self.resource_type,
            {
                "createdAt": "2026-11-16T10:00:00.000Z",
                "message": "Asked for pricing",
                "noteType": "call",
                "pinned": True,
            },
            {
                "creator": {"data": {"type": "user", "id": 7}},
                self.parent: {"data": {"type": self.parent, "id": 42}},
            },
        )

    def expected_record(self, resource_id: int = 1) -> dict:
        return {
            "id": resource_id,
            "createdAt": "2026-11-16T10:00:00.000Z",
            "message": "Asked for pricing",
            "noteType": "call",
            "pinned": True,
            "creator": [7],
            self.parent: [42],
        }


_CASES = [
    NoteCase("prospect_notes", "/prospectNotes", "prospectNote", "prospect", "prospectNotes.read"),
    NoteCase("account_notes", "/accountNotes", "accountNote", "account", "accountNotes.read"),
]


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_full_refresh_flattens_record_without_cursor_filter_or_sort(case: NoteCase, http_mocker: HttpMocker) -> None:
    given_token(http_mocker)
    request = case.request()
    http_mocker.get(request, page_response([case.record()]))

    output = read_stream(case.name, SyncMode.full_refresh)

    assert not output.errors
    assert [message.record.data for message in output.records] == [case.expected_record()]
    http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_pagination_follows_links_next_until_it_is_absent(case: NoteCase, http_mocker: HttpMocker) -> None:
    given_token(http_mocker)
    next_url = case.next_page_url("eyJzcCI6ImlkIn0")
    http_mocker.get(case.request(), page_response([case.record(1)], next_url=next_url))
    http_mocker.get(HttpRequest(next_url), page_response([case.record(2)]))

    output = read_stream(case.name, SyncMode.full_refresh)

    assert not output.errors
    assert record_ids(output) == [1, 2]


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_missing_scope_fails_as_config_error_naming_the_scope(case: NoteCase, http_mocker: HttpMocker) -> None:
    # Body captured from a live 403 on a token without the stream's scope.
    detail = f'StatusCode: Forbidden, Wrapped: Forbidden to access resource: missing scope "{case.scope}"'
    given_token(http_mocker)
    http_mocker.get(case.request(), error_response(403, "forbidden", "Forbidden", detail))

    output = read_stream(case.name, SyncMode.full_refresh, expecting_exception=True)

    assert output.records == []
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert output.errors[0].trace.error.message == (
        f"Outreach denied access: {detail} Re-authenticate the source and grant the missing scope, or deselect this stream."
    )


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_discovery_declares_full_refresh_with_id_primary_key(case: NoteCase) -> None:
    config = ConfigBuilder().build()
    discovery = discover(build_source(config), config)

    assert not discovery.errors
    stream = {s.name: s for s in discovery.catalog.catalog.streams}[case.name]
    assert [mode.value for mode in stream.supported_sync_modes] == ["full_refresh"]
    assert stream.source_defined_primary_key == [["id"]]


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_discovered_schema_declares_and_validates_read_records(case: NoteCase, http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().build()
    discovery = discover(build_source(config), config)
    schema = {s.name: s for s in discovery.catalog.catalog.streams}[case.name].json_schema
    given_token(http_mocker)
    http_mocker.get(case.request(), page_response([case.record()]))

    output = read_stream(case.name, SyncMode.full_refresh, config=config)

    assert len(output.records) == 1
    for message in output.records:
        record = message.record.data
        assert record.keys() <= schema["properties"].keys()
        validate(record, schema)
