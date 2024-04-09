#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_gitlab import SourceGitlab
from source_gitlab.streams import GitlabStream


def test_streams(config, requests_mock):
    requests_mock.get("/api/v4/groups", json=[{"id": "g1"}, {"id": "g256"}])
    source = SourceGitlab()
    streams = source.streams(config)
    assert len(streams) == 23
    assert all([isinstance(stream, GitlabStream) for stream in streams])
    groups, projects, *_ = streams
    assert groups.group_ids == ["g1", "g256"]
    assert projects.project_ids == []


@pytest.mark.parametrize(
    "url_mocks",
    (
        (
            {"url": "/api/v4/groups", "json": [{"id": "g1"}]},
            {"url": "/api/v4/groups/g1", "json": [{"id": "g1", "projects": [{"id": "p1", "path_with_namespace": "p1"}]}]},
            {"url": "/api/v4/projects/p1", "json": {"id": "p1"}},
        ),
        ({"url": "/api/v4/groups", "json": []},),
    ),
)
def test_connection_success(config, requests_mock, url_mocks):
    for url_mock in url_mocks:
        requests_mock.get(**url_mock)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), config)
    assert (status, msg) == (True, None)


def test_connection_invalid_projects_and_projects(config_with_project_groups, requests_mock):
    requests_mock.register_uri("GET", "https://gitlab.com/api/v4/groups/g1?per_page=50", status_code=404)
    requests_mock.register_uri("GET", "https://gitlab.com/api/v4/groups/g1/descendant_groups?per_page=50", status_code=404)
    requests_mock.register_uri("GET", "https://gitlab.com/api/v4/projects/p1?per_page=50&statistics=1", status_code=404)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), config_with_project_groups)
    assert (status, msg) == (False, "Groups and/or projects that you provide are invalid or you don't have permission to view it.")


@pytest.mark.parametrize(
    "errror_code, expected_status",
    (
        (500, False),
        (401, False),
    ),
)
def test_connection_fail_due_to_api_error(errror_code, expected_status, config, mocker, requests_mock):
    mocker.patch("time.sleep")
    requests_mock.get("/api/v4/groups", status_code=errror_code)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), config)
    assert status is False
    assert msg.startswith("Unable to connect to Gitlab API with the provided Private Access Token")


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
    requests_mock.get("/api/v4/groups", status_code=500)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), oauth_config)
    assert status is False
    assert msg.startswith("Unable to connect to Gitlab API with the provided credentials")


def test_connection_fail_due_to_expired_access_token_error(oauth_config, requests_mock):
    expected = "Unable to refresh the `access_token`, please re-authenticate in Sources > Settings."
    requests_mock.post("https://gitlab.com/oauth/token", status_code=401)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger("airbyte"), oauth_config)
    assert status is False
    assert expected in msg


def test_connection_refresh_access_token(oauth_config, requests_mock):
    expected = "Unknown error occurred while checking the connection"
    requests_mock.post("https://gitlab.com/oauth/token", status_code=200, json={"access_token": "new access token"})
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger("airbyte"), oauth_config)
    assert status is False
    assert expected in msg


def test_refresh_expired_access_token_on_error(oauth_config, requests_mock):
    test_response = {
        "access_token": "new_access_token",
        "expires_in": 7200,
        "created_at": 1735689600,
        # (7200 + 1735689600).timestamp().to_rfc3339_string() = "2025-01-01T02:00:00+00:00"
        "refresh_token": "new_refresh_token",
    }
    expected_token_expiry_date = "2025-01-01T02:00:00+00:00"
    requests_mock.post("https://gitlab.com/oauth/token", status_code=200, json=test_response)
    requests_mock.get("https://gitlab.com/api/v4/groups?per_page=50", status_code=200, json=[])
    source = SourceGitlab()
    source.check_connection(logging.getLogger("airbyte"), oauth_config)
    # check the updated config values
    assert test_response.get("access_token") == oauth_config.get("credentials").get("access_token")
    assert test_response.get("refresh_token") == oauth_config.get("credentials").get("refresh_token")
    assert expected_token_expiry_date == oauth_config.get("credentials").get("token_expiry_date")


@pytest.mark.parametrize(
    "api_url, deployment_env, expected_message",
    (
        ("http://gitlab.my.company.org", "CLOUD", "Http scheme is not allowed in this environment. Please use `https` instead."),
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


def test_try_refresh_access_token(oauth_config, requests_mock):
    test_response = {
        "access_token": "new_access_token",
        "expires_in": 7200,
        "created_at": 1735689600,
        # (7200 + 1735689600).timestamp().to_rfc3339_string() = "2025-01-01T02:00:00+00:00"
        "refresh_token": "new_refresh_token",
    }
    requests_mock.post("https://gitlab.com/oauth/token", status_code=200, json=test_response)

    expected = {"api_url": "gitlab.com",
                "credentials": {"access_token": "new_access_token",
                                "auth_type": "oauth2.0",
                                "client_id": "client_id",
                                "client_secret": "client_secret",
                                "refresh_token": "new_refresh_token",
                                "token_expiry_date": "2025-01-01T02:00:00+00:00"},
                "start_date": "2021-01-01T00:00:00Z"}

    source = SourceGitlab()
    source._auth_params(oauth_config)
    assert source._try_refresh_access_token(logger=logging.getLogger(), config=oauth_config) == expected
