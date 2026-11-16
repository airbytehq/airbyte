# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import START_CURSOR
from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, record_ids, stream_state


_STREAM = "folder_contents"
_PATH = "v5/objects/folder-contents"
_FIELDS = "id,folderId,folderRef,objectType,objectId,objectName,objectRef,createdAt,updatedAt,createdById,updatedById"


def _request(updated_at_after: str = START_CURSOR) -> PardotRequestBuilder:
    return (
        PardotRequestBuilder.endpoint(_PATH)
        .with_query_param("limit", 1000)
        .with_query_param("fields", _FIELDS)
        .with_query_param("orderBy", "updatedAt ASC")
        .with_query_param("updatedAtAfter", updated_at_after)
    )


def _next_page_request() -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(_PATH).with_query_param("fields", _FIELDS).with_query_param("nextPageToken", "page-2")


def _folder_content(content_id: int, updated_at: str = "2026-03-01T09:00:00-08:00") -> dict[str, Any]:
    return {
        "id": content_id,
        "folderId": 7,
        "objectType": "Email",
        "objectId": 31,
        "objectName": "Welcome",
        "createdAt": "2026-02-01T08:00:00-08:00",
        "updatedAt": updated_at,
        "createdById": 11,
        "updatedById": 11,
    }


class TestFolderContentsStream(TestCase):
    @HttpMocker()
    def test_first_sync_reads_two_pages_and_saves_the_start_date(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(),
            page_response([_folder_content(number) for number in range(1, 1001)], next_page_url=_next_page_request().url()),
        )
        http_mocker.get(
            _next_page_request().build(),
            page_response([_folder_content(1001), _folder_content(1002, updated_at="2026-03-01T09:00:05-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1003))
        assert output.records[0].record.data == _folder_content(1)
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert stream_state(output) == {"updatedAt": START_CURSOR}

    @HttpMocker()
    def test_restarts_after_a_full_page_without_a_next_page_url(self, http_mocker: HttpMocker) -> None:
        last_of_page = _folder_content(1000, updated_at="2026-03-01T09:16:40-08:00")
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_folder_content(number) for number in range(1, 1000)] + [last_of_page]))
        http_mocker.get(
            _request(updated_at_after="2026-03-01T09:16:40-08:00").build(),
            page_response([_folder_content(1001, updated_at="2026-03-01T09:16:41-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1002))
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_second_sync_sends_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM, {"updatedAt": "2026-03-01T09:00:05-12:00"}).build()
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request(updated_at_after="2026-03-01T09:00:05-12:00").build(),
            page_response([_folder_content(1003, updated_at="2026-03-02T10:30:00-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert record_ids(output) == [1003]
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert stream_state(output) == {"updatedAt": "2026-03-02T10:30:00-12:00"}
