# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .conftest import get_source


_CONFIG = {
    "api_token": "test_token",
    "replication_start_date": "2024-01-01 00:00:00",
}
_MAIL_THREADS_URL = "https://api.pipedrive.com/v1/mailbox/mailThreads"
_MAIL_MESSAGES_URL = f"{_MAIL_THREADS_URL}/1/mailMessages"


def _request(url, query_params):
    return HttpRequest(url, query_params=query_params)


def _response(body):
    return HttpResponse(body=json.dumps(body), status_code=200)


def _mock_mail_threads(http_mocker):
    http_mocker.get(
        _request(
            _MAIL_THREADS_URL,
            {"api_token": "test_token", "limit": "50", "folder": "inbox"},
        ),
        _response(
            {
                "success": True,
                "data": [{"id": 1, "subject": "t"}],
                "additional_data": {
                    "pagination": {
                        "start": 0,
                        "limit": 50,
                        "more_items_in_collection": False,
                    }
                },
            }
        ),
    )
    for folder in ("drafts", "sent", "archive"):
        http_mocker.get(
            _request(
                _MAIL_THREADS_URL,
                {"api_token": "test_token", "limit": "50", "folder": folder},
            ),
            _response({"success": True, "data": []}),
        )


def test_mail_stream_paginates_when_additional_data_missing():
    with HttpMocker() as http_mocker:
        _mock_mail_threads(http_mocker)
        http_mocker.get(
            _request(_MAIL_MESSAGES_URL, {"api_token": "test_token", "limit": "50"}),
            _response(
                {
                    "success": True,
                    "data": [
                        {"id": 10, "subject": "m1"},
                        {"id": 11, "subject": "m2"},
                    ],
                }
            ),
        )

        catalog = CatalogBuilder().with_stream("mail", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert [record.record.data["id"] for record in output.records] == [10, 11]
        assert not output.errors


def test_mail_stream_follows_next_start():
    with HttpMocker() as http_mocker:
        _mock_mail_threads(http_mocker)
        http_mocker.get(
            _request(_MAIL_MESSAGES_URL, {"api_token": "test_token", "limit": "50"}),
            _response(
                {
                    "success": True,
                    "data": [{"id": 10}],
                    "additional_data": {
                        "pagination": {
                            "start": 0,
                            "limit": 50,
                            "more_items_in_collection": True,
                            "next_start": 50,
                        }
                    },
                }
            ),
        )
        http_mocker.get(
            _request(
                _MAIL_MESSAGES_URL,
                {"api_token": "test_token", "limit": "50", "start": "50"},
            ),
            _response(
                {
                    "success": True,
                    "data": [{"id": 11}],
                    "additional_data": {
                        "pagination": {
                            "start": 50,
                            "limit": 50,
                            "more_items_in_collection": False,
                        }
                    },
                }
            ),
        )

        catalog = CatalogBuilder().with_stream("mail", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert [record.record.data["id"] for record in output.records] == [10, 11]
        assert not output.errors
