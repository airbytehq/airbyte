# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import OutreachRequestBuilder
from .response_builder import page_response, resource
from .utils import given_token, read_stream, record_ids, stream_state


_STREAM = "templates"
_PATH = "/templates"


def _request() -> OutreachRequestBuilder:
    return OutreachRequestBuilder.endpoint(_PATH)


def _template(resource_id: int, updated_at: str) -> dict:
    return resource(
        resource_id,
        "template",
        {
            "name": "Follow up",
            "containsCustomHtml": False,
            "hasAiContent": False,
            "personalizationIds": [],
            "updatedAt": updated_at,
        },
        {
            "owner": {"data": {"type": "owner", "id": 7}},
        },
    )


class TestTemplatesStream(TestCase):
    @HttpMocker()
    def test_full_refresh_flattens_attributes_and_relationships(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(_request().build(), page_response([_template(1, "2024-01-02T03:04:05.000Z")]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert [record.record.data for record in output.records] == [
            {
                "id": 1,
                "name": "Follow up",
                "containsCustomHtml": False,
                "hasAiContent": False,
                "personalizationIds": [],
                "updatedAt": "2024-01-02T03:04:05.000Z",
                "owner": [7],
            }
        ]

    @HttpMocker()
    def test_pagination_follows_links_next_until_it_is_absent(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        next_url = _request().next_page_url("eyJzcCI6InVwZGF0ZWRBdCJ9")
        http_mocker.get(_request().build(), page_response([_template(1, "2024-01-02T03:04:05.000Z")], next_url=next_url))
        http_mocker.get(HttpRequest(next_url), page_response([_template(2, "2024-01-03T03:04:05.000Z")]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [1, 2]

    @HttpMocker()
    def test_incremental_first_sync_starts_at_start_date_and_emits_state(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(
            _request().build(),
            page_response([_template(1, "2024-01-02T03:04:05.000Z"), _template(2, "2024-01-03T03:04:05.123Z")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert not output.errors
        assert record_ids(output) == [1, 2]
        assert stream_state(output) == {"updatedAt": "2024-01-03T03:04:05.123Z"}

    @HttpMocker()
    def test_incremental_with_state_requests_from_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM, {"updatedAt": "2024-01-03T03:04:05.123Z"}).build()
        given_token(http_mocker)
        http_mocker.get(
            _request().with_updated_since("2024-01-03T03:04:05.123Z").build(),
            page_response([_template(3, "2024-02-01T00:00:00.000Z")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert not output.errors
        assert record_ids(output) == [3]
        assert stream_state(output) == {"updatedAt": "2024-02-01T00:00:00.000Z"}
