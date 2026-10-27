# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from urllib.parse import urlencode

import pytest
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import _YAML_FILE_PATH
from unit_tests.conftest import build_source as get_source


_BASE_URL = "https://api.outreach.io/api/v2"
_TOKEN_URL = "https://api.outreach.io/oauth/token"
_START_DATE = "2020-11-16T00:00:00Z"
_START_CURSOR = "2020-11-16T00:00:00.000Z"
_CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": _START_DATE,
}

_MANIFEST = yaml.safe_load(Path(_YAML_FILE_PATH).read_text())
_STREAMS = _MANIFEST["definitions"]["streams"]


def _legacy_flatten(element: dict) -> dict:
    relationships = dict()
    for r_type, relations in element.get("relationships", {}).items():
        if relations.get("data"):
            data = relations.get("data", [])
            if isinstance(data, dict):
                data = [data]
            relationships[f"{r_type}"] = [e.get("id") for e in data]

    return {**element.get("attributes"), **{"id": element["id"], **relationships}}


def _query_params(stream_name: str, cursor: str = _START_CURSOR, page: int | None = None) -> dict:
    stream = _STREAMS[stream_name]
    requester = stream["retriever"]["requester"]
    query_params = {
        **requester["request_parameters"],
        stream["incremental_sync"]["start_time_option"]["field_name"]: cursor,
    }
    if page is not None:
        query_params["page[number]"] = str(page)
    return query_params


def _request(stream_name: str, cursor: str = _START_CURSOR, page: int | None = None) -> HttpRequest:
    requester = _STREAMS[stream_name]["retriever"]["requester"]
    return HttpRequest(
        f"{_BASE_URL}{requester['path']}",
        query_params=_query_params(stream_name, cursor, page),
    )


def _response(data: list[dict] | None = None, *, include_data: bool = True, links: dict | None = None) -> HttpResponse:
    body = {}
    if include_data:
        body["data"] = data or []
    if links is not None:
        body["links"] = links
    return HttpResponse(body=json.dumps(body), status_code=200)


def _resource(resource_id: str, attributes: dict | None = None, relationships: dict | None = None) -> dict:
    resource = {
        "id": resource_id,
        "type": "accounts",
        "attributes": attributes or {},
        "links": {"self": f"/accounts/{resource_id}"},
    }
    if relationships is not None:
        resource["relationships"] = relationships
    return resource


def _mock_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        HttpRequest(
            _TOKEN_URL,
            body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
        ),
        HttpResponse(body='{"access_token":"test-access-token","expires_in":3600}', status_code=200),
    )


def _read(
    http_mocker: HttpMocker,
    stream_name: str,
    response: HttpResponse,
    *,
    state=None,
    sync_mode: SyncMode = SyncMode.incremental,
    cursor: str = _START_CURSOR,
) -> object:
    _mock_token(http_mocker)
    http_mocker.get(_request(stream_name, cursor), response)
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    state = state if state is not None else StateBuilder().build()
    return read(get_source(config=_CONFIG, state=state), _CONFIG, catalog, state)


def _assert_matches_legacy(output, resources: list[dict]) -> None:
    actual = [record.record.data for record in output.records]
    assert actual == [_legacy_flatten(resource) for resource in resources]
    for record in actual:
        assert not {"_flat", "attributes", "relationships", "type", "links"}.intersection(record)


@pytest.mark.parametrize("stream_name", sorted(_STREAMS))
def test_all_streams_flatten_jsonapi_records_exactly(stream_name: str) -> None:
    resources = [
        _resource(
            "account-1",
            {
                "name": "Ada",
                "owner": "attribute-owner",
                "updatedAt": "2021-01-01T00:00:00.000Z",
            },
            {
                "owner": {"data": {"id": "user-1", "type": "users"}},
                "teams": {"data": [{"id": "team-1"}, {"id": "team-2"}]},
            },
        ),
        _resource(
            "account-2",
            {"name": "Grace", "updatedAt": "2021-01-02T00:00:00.000Z"},
            {"empty": {"data": []}, "missing": {"links": {"related": "/accounts/2/missing"}}},
        ),
        _resource(
            "account-3",
            {"name": "Katherine", "updatedAt": "2021-01-03T00:00:00.000Z"},
            {"none": {"data": None}, "contact": {"data": [{"id": "prospect-1"}]}},
        ),
    ]
    with HttpMocker() as http_mocker:
        output = _read(http_mocker, stream_name, _response(resources))

    assert not output.errors
    _assert_matches_legacy(output, resources)


@pytest.mark.parametrize(
    "resource",
    [
        pytest.param(
            _resource("dict", {"updatedAt": "2021-01-01T00:00:00.000Z"}, {"related": {"data": {"id": "one"}}}),
            id="relationship-data-object",
        ),
        pytest.param(
            _resource(
                "list",
                {"updatedAt": "2021-01-01T00:00:00.000Z"},
                {"related": {"data": [{"id": "one"}, {"id": "two"}]}},
            ),
            id="relationship-data-list",
        ),
        pytest.param(
            _resource("empty-list", {"updatedAt": "2021-01-01T00:00:00.000Z"}, {"related": {"data": []}}),
            id="relationship-empty-list",
        ),
        pytest.param(
            _resource("null", {"updatedAt": "2021-01-01T00:00:00.000Z"}, {"related": {"data": None}}),
            id="relationship-null",
        ),
        pytest.param(
            _resource(
                "links-only",
                {"updatedAt": "2021-01-01T00:00:00.000Z"},
                {"related": {"links": {"related": "/accounts/links-only/related"}}},
            ),
            id="relationship-links-only",
        ),
        pytest.param(
            _resource(
                "missing-related-id",
                {"updatedAt": "2021-01-01T00:00:00.000Z"},
                {"related": {"data": [{}]}},
            ),
            id="relationship-item-missing-id",
        ),
        pytest.param(
            _resource("no-relationships", {"updatedAt": "2021-01-01T00:00:00.000Z"}),
            id="resource-without-relationships",
        ),
        pytest.param(
            _resource(
                "collision",
                {"related": "attribute-value", "updatedAt": "2021-01-01T00:00:00.000Z"},
                {"related": {"data": {"id": "relationship-value"}}},
            ),
            id="relationship-wins-attribute-collision",
        ),
        pytest.param(
            _resource("top-level-id", {"id": "attribute-id", "updatedAt": "2021-01-01T00:00:00.000Z"}),
            id="top-level-id-wins",
        ),
        pytest.param(
            _resource(
                "values",
                {
                    "updatedAt": "2021-01-01T00:00:00.000Z",
                    "float": 3.125,
                    "bool": False,
                    "nested": {"list": [1, {"inner": "value", "null": None}]},
                    "quoted": """double "quotes", apostrophe's, backslash \\ and newline\nUnicode: café 🐛""",
                    "jinja": "{{ 1 + 1 }}",
                    "none_string": "None",
                    "true_string": "True",
                    "list_string": "[1, 2]",
                },
            ),
            id="attribute-values-round-trip",
        ),
    ],
)
def test_accounts_edge_cases_match_legacy(resource: dict) -> None:
    with HttpMocker() as http_mocker:
        output = _read(http_mocker, "accounts", _response([resource]))

    assert not output.errors
    _assert_matches_legacy(output, [resource])
    if resource["id"] == "missing-related-id":
        assert output.records[0].record.data["related"] == [None]
    if resource["id"] == "collision":
        assert output.records[0].record.data["related"] == ["relationship-value"]
    if resource["id"] == "top-level-id":
        assert output.records[0].record.data["id"] == "top-level-id"


@pytest.mark.parametrize(
    "response",
    [
        pytest.param(_response([]), id="empty-data-array"),
        pytest.param(_response(include_data=False), id="body-without-data"),
    ],
)
def test_empty_or_missing_data_emits_no_records(response: HttpResponse) -> None:
    with HttpMocker() as http_mocker:
        output = _read(http_mocker, "accounts", response)

    assert not output.errors
    assert output.records == []


def test_follows_full_next_url_and_reads_both_pages() -> None:
    first = _resource("page-1", {"name": "first", "updatedAt": "2021-01-01T00:00:00.000Z"})
    second = _resource("page-2", {"name": "second", "updatedAt": "2021-01-02T00:00:00.000Z"})
    base_request = _request("accounts")
    next_query = {**_query_params("accounts"), "page[number]": "2"}
    next_url = f"{_BASE_URL}/accounts?{urlencode(next_query)}"
    second_page_request = HttpRequest(next_url)

    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            base_request,
            _response([first], links={"next": next_url}),
        )
        http_mocker.get(second_page_request, _response([second]))
        catalog = CatalogBuilder().with_stream("accounts", SyncMode.incremental).build()
        state = StateBuilder().build()
        output = read(get_source(config=_CONFIG, state=state), _CONFIG, catalog, state)

    assert not output.errors
    _assert_matches_legacy(output, [first, second])


def test_incremental_state_replay_uses_saved_cursor_and_advances_to_max_record() -> None:
    saved_cursor = "2021-05-06T07:08:09.123Z"
    resources = [
        _resource("older", {"updatedAt": "2021-05-06T08:00:00.456Z"}),
        _resource("newer", {"updatedAt": "2021-05-07T09:10:11.789Z"}),
    ]
    state = StateBuilder().with_stream_state("accounts", {"updatedAt": saved_cursor}).build()

    with HttpMocker() as http_mocker:
        output = _read(http_mocker, "accounts", _response(resources), state=state, cursor=saved_cursor)

    assert not output.errors
    assert [record.record.data for record in output.records] == [_legacy_flatten(resource) for resource in resources]
    assert output.state_messages[-1].state.stream.stream_state.updatedAt == "2021-05-07T09:10:11.789Z"


def test_manifest_has_no_custom_components() -> None:
    manifest_text = Path(_YAML_FILE_PATH).read_text()
    manifest = yaml.safe_load(manifest_text)

    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                yield key, child
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)

    assert all(key != "class_name" for key, _ in walk(manifest))
    assert all(not value.startswith("Custom") for key, value in walk(manifest) if key == "type" and isinstance(value, str))
    assert not (Path(_YAML_FILE_PATH).parent / "components.py").exists()
