# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import _run_command, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def _check(config, tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    return _run_command(get_source(config=config), ["check", "--config", str(config_path)])


@pytest.mark.parametrize(
    "jobs",
    [{}, {"jobs": [{"id": "job-basic", "reportTypeId": "channel_basic_a3"}]}],
    ids=["no-jobs", "no-retired-report"],
)
def test_check_succeeds_without_retired_report(jobs, tmp_path):
    config = ConfigBuilder().build()
    create_job_request = YoutubeAnalyticsRequestBuilder.create_job_request("channel_annotations_a1")
    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(), HttpResponse(body=json.dumps(jobs)))
        http_mocker.post(
            create_job_request,
            HttpResponse(body="{}"),
        )
        output = _check(config, tmp_path)

    assert output.connection_status_messages[0].connectionStatus.status == Status.SUCCEEDED, output.connection_status_messages
    assert output.errors == []
    http_mocker.assert_number_of_calls(create_job_request, 0)


def test_check_rejected_credentials_is_config_error(tmp_path):
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(status_code=401, body=json.dumps({"error": {"code": 401, "message": "invalid authentication credentials"}})),
        )
        output = _check(config, tmp_path)
        read_output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream("jobs", SyncMode.full_refresh).build(),
        )

    assert output.connection_status_messages[0].connectionStatus.status == Status.FAILED
    assert read_output.errors[0].trace.error.failure_type == FailureType.config_error
    assert "Google rejected the YouTube Reporting API credentials" in output.connection_status_messages[0].connectionStatus.message
