# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from unittest import TestCase

import yaml
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_secret": "test-key"}
_COLLECTIONS_REQUEST = HttpRequest(url="https://api.appfollow.io/api/v2/account/apps")
_APP_LISTS_REQUEST = HttpRequest(
    url="https://api.appfollow.io/api/v2/account/apps/app",
    query_params={"apps_id": "1"},
)
_RATINGS_REQUEST = HttpRequest(
    url="https://api.appfollow.io/api/v2/meta/ratings",
    query_params={"ext_id": "123"},
)
_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"


def test_ratings_error_handler_is_default_with_400_ignored():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    error_handler = manifest["definitions"]["streams"]["ratings"]["retriever"]["requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"
    assert error_handler["response_filters"] == [{"type": "HttpResponseFilter", "http_codes": [400], "action": "IGNORE"}]


def _mock_parent_requests(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        _COLLECTIONS_REQUEST,
        HttpResponse(body=json.dumps({"apps": [{"id": 1, "title": "Example"}]}), status_code=200),
    )
    http_mocker.get(
        _APP_LISTS_REQUEST,
        HttpResponse(
            body=json.dumps({"apps_app": [{"app": {"ext_id": "123", "name": "Example app"}}]}),
            status_code=200,
        ),
    )


def _read_ratings() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("ratings", SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


class RatingsStreamTest(TestCase):
    @HttpMocker()
    def test_ratings_stream_emits_records(self, http_mocker: HttpMocker):
        _mock_parent_requests(http_mocker)
        http_mocker.get(
            _RATINGS_REQUEST,
            HttpResponse(
                body=json.dumps(
                    {
                        "ratings": {
                            "ext_id": "123",
                            "list": [
                                {
                                    "version": "1.0",
                                    "country": "US",
                                    "date": "2026-01-01",
                                    "rating": 4.5,
                                    "stars1": 1,
                                    "stars2": 0,
                                    "stars3": 0,
                                    "stars4": 1,
                                    "stars5": 8,
                                    "stars_total": 10,
                                }
                            ],
                            "store": "ios",
                        }
                    }
                ),
                status_code=200,
            ),
        )

        output = _read_ratings()

        assert output.errors == []
        assert len(output.records) == 1
        assert output.records[0].record.data["ratings"]["ext_id"] == "123"
        assert output.records[0].record.data["ratings"]["list"][0]["rating"] == 4.5

    @HttpMocker()
    def test_ratings_stream_ignores_400_responses(self, http_mocker: HttpMocker):
        _mock_parent_requests(http_mocker)
        http_mocker.get(
            _RATINGS_REQUEST,
            HttpResponse(body=json.dumps({"message": "Ratings unavailable"}), status_code=400),
        )

        output = _read_ratings()

        assert output.errors == []
        assert output.records == []
