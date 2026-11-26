# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any
from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response
from .utils import read_stream, record_ids, stream_state


_STREAM = "email_clicks"
_PATH = "emailClick/version/4/do/query"


def _request(created_after: str = "2024-01-01 00:00:00") -> PardotRequestBuilder:
    return (
        PardotRequestBuilder.endpoint(_PATH)
        .with_query_param("format", "json")
        .with_query_param("output", "bulk")
        .with_query_param("sort_by", "id")
        .with_query_param("sort_order", "ascending")
        .with_query_param("limit", 200)
        .with_query_param("created_after", created_after)
    )


def _email_click(click_id: int, created_at: str = "2026-03-01 09:00:00") -> dict[str, Any]:
    return {
        "id": click_id,
        "prospect_id": 301,
        "url": "https://www.example.com/pricing",
        "list_email_id": 21,
        "email_template_id": 31,
        "created_at": created_at,
    }


def _page_response(email_clicks: list[dict[str, Any]]) -> HttpResponse:
    body = {"@attributes": {"stat": "ok", "version": 1}, "result": {"emailClick": email_clicks}}
    return HttpResponse(body=json.dumps(body), status_code=200)


class TestEmailClicksStream(TestCase):
    @HttpMocker()
    def test_first_sync_reads_two_pages_and_saves_the_newest_created_at(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), _page_response([_email_click(number) for number in range(1, 201)]))
        http_mocker.get(
            _request().with_query_param("id_greater_than", 200).build(),
            _page_response([_email_click(201), _email_click(202, created_at="2026-03-01 09:00:05")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 203))
        assert output.records[0].record.data == _email_click(1)
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert stream_state(output) == {"created_at": "2026-03-01 09:00:05"}

    @HttpMocker()
    def test_second_sync_sends_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM, {"created_at": "2026-03-01 09:00:05"}).build()
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request(created_after="2026-03-01 09:00:05").build(),
            _page_response([_email_click(203, created_at="2026-03-02 10:30:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert record_ids(output) == [203]
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert stream_state(output) == {"created_at": "2026-03-02 10:30:00"}
