#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging

import jsonschema
import pytest
import requests_mock
from _helpers import get_source
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API = YoutubeAnalyticsRequestBuilder.BASE_URL
_TOKEN_URL = YoutubeAnalyticsRequestBuilder.TOKEN_URL


@pytest.mark.parametrize("content_owner_id", [None, "owner-1"])
def test_check_lists_report_types_without_listing_or_creating_jobs(config, content_owner_id):
    config = dict(config)
    if content_owner_id:
        config["content_owner_id"] = content_owner_id

    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{_API}/reportTypes", json={"reportTypes": [{"id": "channel_basic_a3", "name": "User activity"}]})
        mocker.get(f"{_API}/jobs", json={"jobs": [{"id": "retired-job", "reportTypeId": "channel_annotations_a1"}]})
        mocker.get(f"{_API}/jobs/retired-job/reports", json={})

        result = get_source(config).check(logging.getLogger("test"), config)

    assert result.status == Status.SUCCEEDED, result.message
    assert [(request.method, request.url.split("?")[0]) for request in mocker.request_history] == [
        ("POST", _TOKEN_URL),
        ("GET", f"{_API}/reportTypes"),
    ]
    request = mocker.request_history[-1]
    assert request.qs == ({"onbehalfofcontentowner": [content_owner_id]} if content_owner_id else {})
    assert request.headers["Authorization"] == "Bearer token"


@pytest.mark.parametrize("content_owner_id", [None, "owner-1"])
def test_report_types_read_paginates_and_records_conform_to_discovered_schema(config, content_owner_id):
    config = dict(config)
    if content_owner_id:
        config["content_owner_id"] = content_owner_id
    first = {"id": "channel_basic_a3", "name": "User activity", "systemManaged": False}
    second = {
        "id": "channel_annotations_a1",
        "name": "Annotations",
        "deprecateTime": "2025-10-31T00:00:00Z",
        "systemManaged": False,
    }
    source = get_source(config)
    catalog = CatalogBuilder().with_stream("report_types", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(
            f"{_API}/reportTypes",
            [
                {"json": {"reportTypes": [first], "nextPageToken": "page-2"}},
                {"json": {"reportTypes": [second]}},
            ],
        )
        output = read(source, config, catalog)
        discovered = source.discover(logging.getLogger("test"), config)

    assert output.errors == []
    assert [record.record.data for record in output.records] == [first, second]
    owner_query = {"onbehalfofcontentowner": [content_owner_id]} if content_owner_id else {}
    assert [(request.method, request.url.split("?")[0], request.qs) for request in mocker.request_history] == [
        ("POST", _TOKEN_URL, {}),
        ("GET", f"{_API}/reportTypes", owner_query),
        ("GET", f"{_API}/reportTypes", {**owner_query, "pagetoken": ["page-2"]}),
    ]
    schema = next(stream.json_schema for stream in discovered.streams if stream.name == "report_types")
    for record in output.records:
        assert record.record.data.keys() <= schema["properties"].keys()
        jsonschema.validate(record.record.data, schema, format_checker=jsonschema.FormatChecker())


@pytest.mark.parametrize(
    "status_code, vendor_message, expected_message",
    [
        (401, "Request had invalid authentication credentials.", "Google rejected the YouTube Reporting API credentials"),
        (403, "The caller does not have permission.", "The YouTube Reporting API denied access"),
    ],
)
def test_check_rejects_report_types_permission_errors_without_retry(config, status_code, vendor_message, expected_message):
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        for path in ("reportTypes", "jobs"):
            mocker.get(f"{_API}/{path}", status_code=status_code, json={"error": {"code": status_code, "message": vendor_message}})

        result = get_source(config).check(logging.getLogger("test"), config)

    assert result.status == Status.FAILED
    assert expected_message in result.message
    assert vendor_message in result.message
    assert [(request.method, request.url) for request in mocker.request_history] == [
        ("POST", _TOKEN_URL),
        ("GET", f"{_API}/reportTypes"),
    ]
