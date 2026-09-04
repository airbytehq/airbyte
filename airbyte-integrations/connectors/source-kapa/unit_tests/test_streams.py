# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime
from urllib.parse import parse_qs, urlparse

from conftest import build_source, load_response

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


THREADS_URL = "https://api.kapa.ai/query/v1/projects/d7b46c01-32a3-4f74-80d3-616a3c18fb6b/threads/"


def read_threads(config, state=None, expecting_exception=False):
    catalog = CatalogBuilder().with_stream("threads", SyncMode.incremental).build()
    state = StateBuilder().build() if state is None else state
    return read(build_source(config, state), config, catalog, state, expecting_exception)


def test_threads_paginates_and_emits_records(config, requests_mock):
    requests_mock.get(
        THREADS_URL,
        [
            {"json": load_response("threads_page_1.json")},
            {"json": load_response("threads_page_2.json")},
        ],
    )

    output = read_threads(config)

    assert [message.record.data["id"] for message in output.records] == [
        "6ea2745a-b70d-42f3-b13c-a4227803a4d7",
        "47edf32e-b71c-4748-ab0b-958414daca2d",
    ]
    assert requests_mock.call_count == 2

    first_request, second_request = requests_mock.request_history
    first_query = parse_qs(urlparse(first_request.url).query)
    second_query = parse_qs(urlparse(second_request.url).query)

    assert first_request.headers["X-API-KEY"] == "test-api-key"
    assert first_request.headers["Accept"] == "application/json"
    assert first_query["page_size"] == ["500"]
    assert first_query["sort"] == ["asc"]
    assert first_query["include"] == ["feedback,status_tag,custom_tags,interaction_tags,end_user,integration"]
    assert "cursor" not in first_query
    assert second_query["cursor"] == ["next-page"]


def test_threads_uses_prior_state_as_inclusive_lower_bound(config, requests_mock):
    requests_mock.get(THREADS_URL, json={"results": [], "next_cursor": None})
    prior_cursor = "2024-02-01T12:30:00.000000+0000"
    state = StateBuilder().with_stream_state("threads", {"last_activity_at": prior_cursor}).build()

    read_threads(config, state)

    query = parse_qs(urlparse(requests_mock.last_request.url).query)
    actual_lower_bound = datetime.fromisoformat(query["updated_since"][0])
    assert actual_lower_bound == datetime.fromisoformat(prior_cursor)
