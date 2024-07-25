#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import logging

import pytest
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from source_gitlab import SourceGitlab


def test_streams(config):
    source = SourceGitlab()
    streams = source.streams(config)
    assert len(streams) == 23
    assert all([isinstance(stream, DeclarativeStream) for stream in streams])


def test_connection_success(config, requests_mock):
    requests_mock.get(url="/api/v4/groups", json=[{"id": "g1"}])
    requests_mock.get(
        url="/api/v4/groups/g1", json=[{"id": "g1", "projects": [{"id": "p1", "path_with_namespace": "p1"}]}]
    )
    requests_mock.get(url="/api/v4/projects/p1", json={"id": "p1"})
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), config)
    assert (status, msg) == (True, None)


def test_connection_invalid_projects_and_projects(config_with_project_groups, requests_mock):
    requests_mock.register_uri("GET", "https://gitlab.com/api/v4/groups/g1?per_page=50", status_code=404)
    requests_mock.register_uri(
        "GET", "https://gitlab.com/api/v4/groups/g1/descendant_groups?per_page=50", status_code=404
    )
    requests_mock.register_uri("GET", "https://gitlab.com/api/v4/projects/p1?per_page=50&statistics=1", status_code=404)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), config_with_project_groups)
    assert status is False
    assert msg == (
        "Unable to connect to stream projects - "
        "Groups and/or projects that you provide are invalid or you don't have permission to view it."
    )


def test_connection_fail_due_to_api_error(config, mocker, requests_mock):
    mocker.patch("time.sleep")
    error_code = 401
    requests_mock.get("/api/v4/groups", status_code=error_code)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), config)
    assert status is False
    assert msg == (
        "Unable to connect to stream projects - Unable to refresh the `access_token`, "
        "please re-authenticate in Sources > Settings."
    )


def test_connection_fail_due_to_api_error_oauth(oauth_config, mocker, requests_mock):
    mocker.patch("time.sleep")
    test_response = {
        "access_token": "new_access_token",
        "expires_in": 7200,
        "created_at": 1735689600,
        # (7200 + 1735689600).timestamp().to_rfc3339_string() = "2025-01-01T02:00:00+00:00"
        "refresh_token": "new_refresh_token",
    }
    requests_mock.post("https://gitlab.com/oauth/token", status_code=200, json=test_response)
    requests_mock.get("/api/v4/groups", status_code=401)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), oauth_config)
    assert status is False
    assert msg == (
        "Unable to connect to stream projects - Unable to refresh the `access_token`, "
        "please re-authenticate in Sources > Settings."
    )


@pytest.mark.parametrize(
    "api_url, deployment_env, expected_message",
    (
        (
            "http://gitlab.my.company.org",
            "CLOUD",
            "Http scheme is not allowed in this environment. Please use `https` instead.",
        ),
        ("https://gitlab.com/api/v4", "CLOUD", "Invalid API resource locator."),
    ),
)
def test_connection_fail_due_to_config_error(mocker, api_url, deployment_env, expected_message):
    mocker.patch("os.environ", {"DEPLOYMENT_MODE": deployment_env})
    source = SourceGitlab()
    config = {
        "start_date": "2021-01-01T00:00:00Z",
        "api_url": api_url,
        "credentials": {"auth_type": "access_token", "access_token": "token"},
    }
    status, msg = source.check_connection(logging.getLogger(), config)
    assert (status, msg) == (False, expected_message)
