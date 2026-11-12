# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def _authenticate(http_mocker):
    http_mocker.post(
        YoutubeAnalyticsRequestBuilder.token_request(),
        HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
    )


@pytest.mark.parametrize("content_owner_id", [None, "owner-1"])
def test_check_empty_jobs_succeeds_without_creating_jobs(content_owner_id):
    config = ConfigBuilder().with_content_owner_id(content_owner_id).build()
    jobs = YoutubeAnalyticsRequestBuilder.jobs_endpoint()
    if content_owner_id:
        jobs.with_on_behalf_of_content_owner(content_owner_id)
    request = jobs.build()
    with HttpMocker() as http_mocker:
        _authenticate(http_mocker)
        http_mocker.get(request, HttpResponse(body="{}"))

        result = get_source(config).check(logging.getLogger("test"), config)

        assert result.status == Status.SUCCEEDED, result.message
        http_mocker.assert_number_of_calls(request, 1)


def test_check_jobs_access_denied_preserves_message():
    config = ConfigBuilder().build()
    request = YoutubeAnalyticsRequestBuilder.jobs_endpoint().build()
    with HttpMocker() as http_mocker:
        _authenticate(http_mocker)
        http_mocker.get(
            request,
            HttpResponse(body=json.dumps({"error": {"code": 403, "message": "Insufficient permissions"}}), status_code=403),
        )

        result = get_source(config).check(logging.getLogger("test"), config)

        assert result.status == Status.FAILED
        assert "The YouTube Reporting API denied access: Insufficient permissions" in result.message
        http_mocker.assert_number_of_calls(request, 1)


def test_read_jobs_paginates_without_filtering_or_creating_jobs():
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream("reporting_jobs", SyncMode.full_refresh).build()
    first_page = YoutubeAnalyticsRequestBuilder.jobs_endpoint().build()
    second_page = YoutubeAnalyticsRequestBuilder.jobs_endpoint().with_query_param("pageToken", "page-2").build()
    jobs = [
        {"id": "job-1", "reportTypeId": "channel_basic_a3", "name": "Basic report", "systemManaged": False},
        {"id": "job-2", "reportTypeId": "channel_combined_a3", "createTime": "2026-01-01T00:00:00Z"},
    ]
    with HttpMocker() as http_mocker:
        _authenticate(http_mocker)
        http_mocker.get(first_page, HttpResponse(body=json.dumps({"jobs": [jobs[0]], "nextPageToken": "page-2"})))
        http_mocker.get(second_page, HttpResponse(body=json.dumps({"jobs": [jobs[1]]})))

        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        assert [record.record.data for record in output.records] == jobs
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)
