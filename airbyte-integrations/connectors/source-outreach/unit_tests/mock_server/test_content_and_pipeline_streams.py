# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Iterator
from dataclasses import dataclass
from urllib.parse import urlencode

import pytest
from jsonschema import validate

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source

from .config import ConfigBuilder
from .request_builder import BASE_URL, START_CURSOR
from .response_builder import page_response, resource
from .utils import given_token, read_stream, record_ids, stream_state


_CREATED_AT = "2024-01-01T00:00:00.000Z"
_UPDATED_AT = "2024-01-02T03:04:05.000Z"
_SAVED_CURSOR = "2024-01-03T03:04:05.123Z"


@dataclass(frozen=True)
class StreamCase:
    name: str
    path: str
    resource_type: str
    attributes: dict
    relationships: dict
    flattened_relationships: dict[str, list[int]]
    incremental: bool = True

    def record(self, resource_id: int = 1, updated_at: str = _UPDATED_AT) -> dict:
        return resource(resource_id, self.resource_type, {**self.attributes, "updatedAt": updated_at}, self.relationships)

    def expected_record(self, resource_id: int = 1, updated_at: str = _UPDATED_AT) -> dict:
        attributes = {key: value for key, value in self.attributes.items() if value is not None}
        return {"id": resource_id, **attributes, "updatedAt": updated_at, **self.flattened_relationships}

    def query_params(self, cursor: str = START_CURSOR) -> dict[str, str]:
        params = {"count": "false", "page[size]": "1000", "newFilterSyntax": "true"}
        if self.incremental:
            params.update({"sort": "updatedAt", "filter[updatedAt][gte]": cursor})
        return params

    def request(self, cursor: str = START_CURSOR) -> HttpRequest:
        return HttpRequest(f"{BASE_URL}{self.path}", query_params=self.query_params(cursor))


_CASES = [
    StreamCase(
        "sequence_templates",
        "/sequenceTemplates",
        "sequenceTemplate",
        {
            "bounceCount": 0,
            "clickCount": 2,
            "createdAt": _CREATED_AT,
            "deliverCount": 4,
            "enabled": True,
            "enabledAt": _CREATED_AT,
            "failureCount": 0,
            "interestedCount": None,
            "isReply": False,
            "negativeReplyCount": 0,
            "neutralReplyCount": 0,
            "openCount": 3,
            "optOutCount": 0,
            "positiveReplyCount": 1,
            "replyCount": 1,
            "scheduleCount": 4,
        },
        {
            "creator": {"data": {"type": "user", "id": 7}},
            "sequenceStep": {"data": {"type": "sequenceStep", "id": 11}},
            "template": {"data": {"type": "template", "id": 12}},
            "updater": {"data": {"type": "user", "id": 8}},
        },
        {"creator": [7], "sequenceStep": [11], "template": [12], "updater": [8]},
        incremental=False,
    ),
    StreamCase(
        "content_categories",
        "/contentCategories",
        "contentCategory",
        {
            "allowSequences": True,
            "allowSnippets": True,
            "allowTemplates": False,
            "color": "#5951ff",
            "createdAt": _CREATED_AT,
            "name": "Sales content",
            "public": True,
        },
        {
            "creator": {"data": {"type": "user", "id": 7}},
            "teams": {"data": [{"type": "team", "id": 11}, {"type": "team", "id": 12}]},
        },
        {"creator": [7], "teams": [11, 12]},
    ),
    StreamCase(
        "content_category_memberships",
        "/contentCategoryMemberships",
        "contentCategoryMembership",
        {"createdAt": _CREATED_AT},
        {
            "content": {"data": {"type": "sequence", "id": 11}},
            "contentCategory": {"data": {"type": "contentCategory", "id": 12}},
            "creator": {"data": {"type": "user", "id": 7}},
        },
        {"content": [11], "contentCategory": [12], "creator": [7]},
    ),
    StreamCase(
        "content_category_ownerships",
        "/contentCategoryOwnerships",
        "contentCategoryOwnership",
        {"createdAt": _CREATED_AT},
        {
            "contentCategory": {"data": {"type": "contentCategory", "id": 12}},
            "creator": {"data": {"type": "user", "id": 7}},
            "owner": {"data": {"type": "team", "id": 11}},
        },
        {"contentCategory": [12], "creator": [7], "owner": [11]},
    ),
    StreamCase(
        "opportunity_stages",
        "/opportunityStages",
        "opportunityStage",
        {"color": "#5951ff", "createdAt": _CREATED_AT, "isClosed": False, "name": "Qualification", "order": 2},
        {
            "creator": {"data": {"type": "user", "id": 7}},
            "opportunities": {"data": [{"type": "opportunity", "id": 11}, {"type": "opportunity", "id": 12}]},
        },
        {"creator": [7], "opportunities": [11, 12]},
    ),
    StreamCase(
        "opportunity_prospect_roles",
        "/opportunityProspectRoles",
        "opportunityProspectRole",
        {"createdAt": _CREATED_AT, "primary": True, "role": "Decision maker"},
        {
            "opportunity": {"data": {"type": "opportunity", "id": 11}},
            "prospect": {"data": {"type": "prospect", "id": 12}},
        },
        {"opportunity": [11], "prospect": [12]},
    ),
    StreamCase(
        "task_priorities",
        "/taskPriorities",
        "taskPriority",
        {"color": 1, "createdAt": _CREATED_AT, "name": "High", "weight": 3},
        {
            "sequenceSteps": {"data": [{"type": "sequenceStep", "id": 11}]},
            "tasks": {"data": [{"type": "task", "id": 12}, {"type": "task", "id": 13}]},
        },
        {"sequenceSteps": [11], "tasks": [12, 13]},
    ),
]
_INCREMENTAL_CASES = [case for case in _CASES if case.incremental]


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_full_refresh_flattens_exact_record(case: StreamCase, http_mocker: HttpMocker) -> None:
    given_token(http_mocker)
    request = case.request()
    http_mocker.get(request, page_response([case.record()]))

    output = read_stream(case.name, SyncMode.full_refresh)

    assert [record.record.data for record in output.records] == [case.expected_record()]
    assert not output.errors
    http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_pagination_follows_links_next(case: StreamCase, http_mocker: HttpMocker) -> None:
    given_token(http_mocker)
    first_request = case.request()
    next_url = f"{BASE_URL}{case.path}?{urlencode({**case.query_params(), 'page[after]': 'next-page'})}"
    next_request = HttpRequest(next_url)
    http_mocker.get(first_request, page_response([case.record()], next_url=next_url))
    http_mocker.get(next_request, page_response([case.record(2, _SAVED_CURSOR)]))

    output = read_stream(case.name, SyncMode.full_refresh)

    assert record_ids(output) == [1, 2]
    assert not output.errors
    http_mocker.assert_number_of_calls(first_request, 1)
    http_mocker.assert_number_of_calls(next_request, 1)


@pytest.mark.parametrize("case", _INCREMENTAL_CASES, ids=lambda case: case.name)
def test_incremental_first_sync_emits_newest_cursor(case: StreamCase, http_mocker: HttpMocker) -> None:
    given_token(http_mocker)
    request = case.request()
    http_mocker.get(request, page_response([case.record(), case.record(2, _SAVED_CURSOR)]))

    output = read_stream(case.name, SyncMode.incremental)

    assert record_ids(output) == [1, 2]
    assert not output.errors
    assert stream_state(output) == {"updatedAt": _SAVED_CURSOR}
    http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("case", _INCREMENTAL_CASES, ids=lambda case: case.name)
def test_incremental_with_state_requests_saved_cursor(case: StreamCase, http_mocker: HttpMocker) -> None:
    state = StateBuilder().with_stream_state(case.name, {"updatedAt": _SAVED_CURSOR}).build()
    given_token(http_mocker)
    request = case.request(_SAVED_CURSOR)
    newest = "2024-02-01T00:00:00.000Z"
    http_mocker.get(request, page_response([case.record(3, newest)]))

    output = read_stream(case.name, SyncMode.incremental, state=state)

    assert record_ids(output) == [3]
    assert not output.errors
    assert stream_state(output) == {"updatedAt": newest}
    http_mocker.assert_number_of_calls(request, 1)


def test_sequence_templates_full_refresh_has_no_cursor_filter_or_sort(http_mocker: HttpMocker) -> None:
    case = _CASES[0]
    given_token(http_mocker)
    request = HttpRequest(
        f"{BASE_URL}/sequenceTemplates",
        query_params={"count": "false", "page[size]": "1000", "newFilterSyntax": "true"},
    )
    http_mocker.get(request, page_response([case.record()]))

    output = read_stream(case.name, SyncMode.full_refresh)

    assert [record.record.data for record in output.records] == [case.expected_record()]
    assert not output.errors
    http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_discovered_schema_declares_and_validates_read_records(case: StreamCase, http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().build()
    discovery = discover(build_source(config), config)
    assert not discovery.errors
    streams = {stream.name: stream for stream in discovery.catalog.catalog.streams}
    assert case.name in streams, f"{case.name} missing from discovered catalog"
    schema = streams[case.name].json_schema
    given_token(http_mocker)
    request = case.request()
    http_mocker.get(request, page_response([case.record()]))

    output = read_stream(case.name, SyncMode.full_refresh, config=config)

    assert output.records, f"{case.name} emitted no records"
    assert not output.errors
    for message in output.records:
        record = message.record.data
        assert record.keys() <= schema["properties"].keys()
        validate(record, schema)
    http_mocker.assert_number_of_calls(request, 1)
