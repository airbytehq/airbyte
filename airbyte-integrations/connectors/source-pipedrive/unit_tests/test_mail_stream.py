# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_token": "test_token", "replication_start_date": "2024-01-01 00:00:00"}
_MAIL_THREADS_URL = "https://api.pipedrive.com/v1/mailbox/mailThreads"
_MAIL_MESSAGES_URL = f"{_MAIL_THREADS_URL}/1/mailMessages"


def _request(url, query_params):
    return HttpRequest(url, query_params=query_params)


def _response(body):
    return HttpResponse(body=json.dumps(body), status_code=200)


def _page(records, next_start=None):
    pagination = {"start": 0, "limit": 50, "more_items_in_collection": next_start is not None}
    if next_start is not None:
        pagination["next_start"] = next_start
    return {"success": True, "data": records, "additional_data": {"pagination": pagination}}


def _threads_request(folder, start=None):
    params = {"api_token": "test_token", "limit": "50", "folder": folder}
    if start is not None:
        params["start"] = str(start)
    return _request(_MAIL_THREADS_URL, params)


def _mock_empty_folders(http_mocker, folders=("drafts", "sent", "archive")):
    for folder in folders:
        http_mocker.get(_threads_request(folder), _response(_page([])))


def _read(stream):
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


def test_mail_stream_succeeds_when_additional_data_missing():
    # GET /v1/mailbox/mailThreads/{id}/mailMessages returns no additional_data block at all.
    with HttpMocker() as http_mocker:
        http_mocker.get(_threads_request("inbox"), _response(_page([{"id": 1, "subject": "t"}])))
        _mock_empty_folders(http_mocker)
        http_mocker.get(
            _request(_MAIL_MESSAGES_URL, {"api_token": "test_token", "limit": "50"}),
            _response({"success": True, "data": [{"id": 10, "subject": "m1"}, {"id": 11, "subject": "m2"}]}),
        )

        output = _read("mail")

        assert [record.record.data["id"] for record in output.records] == [10, 11]
        assert not output.errors


def test_mail_threads_follow_next_start():
    with HttpMocker() as http_mocker:
        http_mocker.get(_threads_request("inbox"), _response(_page([{"id": 1}], next_start=50)))
        http_mocker.get(_threads_request("inbox", start=50), _response(_page([{"id": 2}])))
        _mock_empty_folders(http_mocker)

        output = _read("mailThreads")

        assert [record.record.data["id"] for record in output.records] == [1, 2]
        assert not output.errors
