#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Dict, Optional

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONTENT_OWNER_ID = "content-owner-1"
_EXISTING_JOB = {"id": "job-1", "reportTypeId": "channel_annotations_a1", "name": "Airbyte reporting job"}


def _check(config: Dict[str, Any]):
    return get_source(config=config).check(logging.getLogger("test"), config)


@pytest.mark.parametrize(
    "jobs_response",
    [
        pytest.param({}, id="account-with-no-reporting-jobs"),
        pytest.param({"jobs": [_EXISTING_JOB]}, id="job-exists-but-has-no-report-files-yet"),
    ],
)
@pytest.mark.parametrize("content_owner_id", [None, _CONTENT_OWNER_ID], ids=["channel", "content-owner"])
def test_check_succeeds_before_youtube_has_generated_any_report(jobs_response: Dict[str, Any], content_owner_id: Optional[str]) -> None:
    """A new source has no report files for up to 48 hours; setup must not depend on them."""
    config_builder = ConfigBuilder()
    jobs_request = YoutubeAnalyticsRequestBuilder.jobs_endpoint()
    reports_request = YoutubeAnalyticsRequestBuilder.reports_endpoint(_EXISTING_JOB["id"]).with_created_after(
        "1990-01-01T00:00:00.000000Z"
    )
    if content_owner_id:
        config_builder = config_builder.with_content_owner_id(content_owner_id)
        jobs_request = jobs_request.with_on_behalf_of_content_owner(content_owner_id)
        reports_request = reports_request.with_on_behalf_of_content_owner(content_owner_id)
    config = config_builder.build()
    jobs_request, reports_request = jobs_request.build(), reports_request.build()
    create_job_request = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        # A string, not a mapping: `HttpRequest` JSON-decodes every candidate body when either
        # side is a mapping, which breaks on the form-encoded token request.
        body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"}),
    )

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(jobs_request, HttpResponse(body=json.dumps(jobs_response)))
        # Not requested by `check`. Registered so that a `check` which does go on to create a
        # job or list report files fails on the assertions below, not on an unmatched request.
        http_mocker.post(create_job_request, HttpResponse(body=json.dumps(_EXISTING_JOB)))
        http_mocker.get(reports_request, HttpResponse(body=json.dumps({})))

        status = _check(config)

        assert status.status == Status.SUCCEEDED, status.message
        http_mocker.assert_number_of_calls(jobs_request, 1)
        # `check` only reads: it must not create a reporting job on the user's account.
        http_mocker.assert_number_of_calls(create_job_request, 0)
        http_mocker.assert_number_of_calls(reports_request, 0)


def test_check_fails_with_the_no_channel_message_when_youtube_rejects_the_account() -> None:
    config = ConfigBuilder().build()
    jobs_request = YoutubeAnalyticsRequestBuilder.jobs_endpoint().build()

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            jobs_request,
            HttpResponse(body=json.dumps({"error": {"code": 401, "message": "Unauthorized", "status": "UNAUTHENTICATED"}}), status_code=401),
        )

        status = _check(config)

        assert status.status == Status.FAILED
        assert "The authorized Google account does not appear to have an associated YouTube channel." in status.message
        http_mocker.assert_number_of_calls(jobs_request, 1)


@pytest.mark.parametrize("content_owner_id", [None, _CONTENT_OWNER_ID], ids=["channel", "content-owner"])
def test_reporting_jobs_emits_every_job_across_pages_without_creating_one(content_owner_id: Optional[str]) -> None:
    config_builder = ConfigBuilder()
    first_page_request = YoutubeAnalyticsRequestBuilder.jobs_endpoint()
    second_page_request = YoutubeAnalyticsRequestBuilder.jobs_endpoint().with_query_param("pageToken", "page-2")
    if content_owner_id:
        config_builder = config_builder.with_content_owner_id(content_owner_id)
        first_page_request = first_page_request.with_on_behalf_of_content_owner(content_owner_id)
        second_page_request = second_page_request.with_on_behalf_of_content_owner(content_owner_id)
    config = config_builder.build()
    first_page_request, second_page_request = first_page_request.build(), second_page_request.build()
    jobs = [
        {"id": "job-1", "reportTypeId": "channel_basic_a3", "name": "Airbyte reporting job", "createTime": "2026-10-01T00:00:00Z"},
        {"id": "job-2", "reportTypeId": "channel_cards_a1", "name": "Another job", "createTime": "2026-10-02T00:00:00Z"},
        {"id": "job-3", "reportTypeId": "playlist_basic_a2", "name": "Airbyte reporting job", "createTime": "2026-10-03T00:00:00Z"},
    ]
    catalog = CatalogBuilder().with_stream("reporting_jobs", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(first_page_request, HttpResponse(body=json.dumps({"jobs": jobs[:2], "nextPageToken": "page-2"})))
        http_mocker.get(second_page_request, HttpResponse(body=json.dumps({"jobs": jobs[2:]})))

        output = read(get_source(config=config), config=config, catalog=catalog)

        assert output.errors == []
        assert [record.record.data for record in output.records] == jobs
        http_mocker.assert_number_of_calls(first_page_request, 1)
        http_mocker.assert_number_of_calls(second_page_request, 1)
