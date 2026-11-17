# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from http import HTTPStatus

import pytest

from airbyte_cdk.test.mock_http import HttpMocker

from .analytics_helpers import APP_ID
from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import error_response, fixture_response, json_response
from .utils import read_output


_STREAM_NAME = "app_store_versions"
_ATTRIBUTES = {"versionString": "1.2", "usesIdfa": False, "downloadable": True, "createdDate": "2024-01-01T00:00:00Z"}


@pytest.mark.parametrize("scenario", ["pages", "empty", "missing"])
def test_app_substream(scenario: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(RequestBuilder.apps_endpoint().build(), fixture_response("list_id_apps"))
        request = RequestBuilder.app_substream_endpoint(APP_ID, "appStoreVersions")
        payload = {"data": [{"id": "record-1", "type": "appStoreVersions", "attributes": _ATTRIBUTES}]}
        if scenario == "pages":
            payload["links"] = {"next": f"{request.url}?cursor=PAGE_TWO"}
            http_mocker.get(request.build(), json_response(payload))
            http_mocker.get(
                RequestBuilder.app_substream_endpoint(APP_ID, "appStoreVersions").with_cursor("PAGE_TWO").build(),
                json_response({"data": [{"id": "record-2", "type": "appStoreVersions", "attributes": _ATTRIBUTES}]}),
            )
        elif scenario == "empty":
            http_mocker.get(request.build(), json_response({"data": []}))
        else:
            http_mocker.get(request.build(), error_response(HTTPStatus.NOT_FOUND))
        output = read_output(ConfigBuilder(), _STREAM_NAME)
        if scenario == "pages":
            assert {record.record.data["id"] for record in output.records} == {"record-1", "record-2"}
            for record in output.records:
                assert record.record.data["app_id"] == APP_ID
                for field, value in _ATTRIBUTES.items():
                    assert record.record.data[field] == value
                assert "attributes" not in record.record.data
        else:
            assert not output.records
