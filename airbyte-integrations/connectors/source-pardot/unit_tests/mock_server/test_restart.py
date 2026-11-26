# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from urllib.parse import parse_qs, quote

import pytest
from conftest import resolved_manifest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, record_ids, sent_queries


# Stream, path, cursor field, and whether the first page of a query sends `deleted=all`.
_RESTARTING_STREAMS = [
    ("campaigns", "v5/objects/campaigns", "updatedAt", True),
    ("custom_fields", "v5/objects/custom-fields", "updatedAt", False),
    ("dynamic_contents", "v5/objects/dynamic-contents", "updatedAt", True),
    ("emails", "v5/objects/emails", "sentAt", False),
    ("engagement_studio_programs", "v5/objects/engagement-studio-programs", "updatedAt", True),
    ("folder_contents", "v5/objects/folder-contents", "updatedAt", False),
    ("form_fields", "v5/objects/form-fields", "updatedAt", False),
    ("landing_pages", "v5/objects/landing-pages", "updatedAt", True),
    ("lifecycle_histories", "v5/objects/lifecycle-histories", "createdAt", False),
    ("lifecycle_stages", "v5/objects/lifecycle-stages", "updatedAt", True),
    ("list_emails", "v5/objects/list-emails", "updatedAt", True),
    ("list_membership", "v5/objects/list-memberships", "updatedAt", True),
    ("lists", "v5/objects/lists", "updatedAt", True),
    ("opportunities", "v5/objects/opportunities", "updatedAt", False),
    ("prospects", "v5/objects/prospects", "updatedAt", True),
    ("tags", "v5/objects/tags", "updatedAt", False),
    ("users", "v5/objects/users", "updatedAt", True),
    ("visitor_activities", "v5/objects/visitor-activities", "updatedAt", False),
    ("visitor_page_views", "v5/objects/visitor-page-views", "createdAt", False),
    ("visits", "v5/objects/visits", "updatedAt", False),
]


def test_the_table_lists_every_stream_that_restarts_on_an_inclusive_filter() -> None:
    restarting = {
        stream["name"]
        for stream in resolved_manifest()["streams"]
        if "AfterOrEqualTo=" in json.dumps(stream["retriever"].get("paginator", {}))
    }

    assert restarting == {stream for stream, *_ in _RESTARTING_STREAMS}


@pytest.mark.parametrize("offset", ["+01:00", "-08:00"])
@pytest.mark.parametrize(
    ("stream", "path", "cursor_field", "sends_deleted"), [pytest.param(*row, id=row[0]) for row in _RESTARTING_STREAMS]
)
def test_restart_sends_one_inclusive_filter_with_the_value_encoded(
    stream: str, path: str, cursor_field: str, sends_deleted: bool, offset: str
) -> None:
    # Past 100,000 records the API returns a full page with no page token, and the connector starts a new query from the
    # last record's cursor value.
    boundary = f"2026-03-01T09:16:40{offset}"
    full_page = [{"id": number, cursor_field: "2026-03-01T09:00:00-08:00"} for number in range(1, 1000)]
    full_page.append({"id": 1000, cursor_field: boundary})
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            PardotRequestBuilder.endpoint(path).with_any_query_params().build(),
            [page_response(full_page), page_response([{"id": 1001, cursor_field: boundary}])],
        )

        output = read_stream(stream, SyncMode.incremental)
        queries = sent_queries(http_mocker)

    assert record_ids(output) == list(range(1, 1002))
    assert len(queries) == 2
    filter_name = f"{cursor_field}AfterOrEqualTo"
    # Percent-encoded: a raw "+" in a query string reads as a space.
    assert queries[1].startswith(f"{filter_name}={quote(boundary, safe='')}&")
    restart = parse_qs(queries[1])
    assert restart[filter_name] == [boundary]
    assert restart["limit"] == ["1000"]
    assert restart["orderBy"] == [f"{cursor_field} ASC"]
    assert restart["fields"]
    assert set(restart) == {filter_name, "limit", "fields", "orderBy"} | ({"deleted"} if sends_deleted else set())
    if sends_deleted:
        assert restart["deleted"] == ["all"]
