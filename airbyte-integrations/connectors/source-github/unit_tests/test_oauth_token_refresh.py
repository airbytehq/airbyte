# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from urllib.parse import parse_qs

import pytest

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .utils import make_source


REFRESH_URL = "https://github.com/login/oauth/access_token"
BRANCHES_URL = "https://api.github.com/repos/org/repo/branches"
EXPIRED = "2020-01-01T00:00:00Z"
NOT_EXPIRED = "2099-01-01T00:00:00Z"


def oauth_config(**credentials_overrides):
    return {
        "credentials": {
            "option_title": "OAuth Credentials",
            "access_token": "stored-access-token",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "refresh_token": "stored-refresh-token",
            "token_expiry_date": EXPIRED,
            **credentials_overrides,
        },
        "repositories": ["org/repo"],
    }


def mock_repository(requests_mock):
    requests_mock.get("https://api.github.com/repos/org/repo", json={"full_name": "org/repo", "default_branch": "main"})
    return requests_mock.get(BRANCHES_URL, json=[{"name": "main", "commit": {"sha": "abc"}}])


def mock_refresh(requests_mock, **kwargs):
    kwargs.setdefault(
        "json",
        {
            "access_token": "new-access-token",
            "expires_in": 28800,
            "refresh_token": "new-refresh-token",
            "refresh_token_expires_in": 15897600,
            "scope": "",
            "token_type": "bearer",
        },
    )
    return requests_mock.post(REFRESH_URL, **kwargs)


def emitted_configs(capsys):
    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith('{"type":"CONTROL"')]
    return [message["control"]["connectorConfig"]["config"] for message in messages]


def read_branches(source):
    stream = next(stream for stream in source.streams(source._config) if stream.name == "branches")
    return [record for partition in stream.generate_partitions() for record in partition.read()]


@pytest.mark.parametrize(
    "config, expected",
    [
        pytest.param(oauth_config(), "enabled", id="oauth_with_refresh_token"),
        pytest.param(oauth_config(token_expiry_date=None), "enabled", id="oauth_with_refresh_token_and_no_expiry_date"),
        pytest.param(oauth_config(refresh_token=None), "disabled", id="oauth_with_null_refresh_token"),
        pytest.param(oauth_config(refresh_token=""), "disabled", id="oauth_with_empty_refresh_token"),
        pytest.param(oauth_config(client_secret=""), "disabled", id="oauth_without_client_secret"),
        pytest.param(oauth_config(client_id=""), "disabled", id="oauth_without_client_id"),
        pytest.param({**oauth_config(), "access_token": "legacy-token"}, "disabled", id="legacy_root_access_token_wins"),
        pytest.param(
            {**oauth_config(), "api_url": "https://github.example.com/api/v3"}, "disabled", id="github_enterprise_server_api_url"
        ),
        pytest.param({**oauth_config(), "api_url": "https://api.octocorp.ghe.com"}, "disabled", id="data_residency_api_url"),
        pytest.param({**oauth_config(), "api_url": "https://api.github.com"}, "enabled", id="github_com_api_url_without_slash"),
        pytest.param(
            {"credentials": {"option_title": "PAT Credentials", "personal_access_token": "pat"}, "repositories": ["org/repo"]},
            "disabled",
            id="personal_access_token",
        ),
    ],
)
def test_token_refresh_is_enabled_only_for_a_complete_github_com_oauth_config(config, expected):
    assert make_source(config=config)._config["oauth_token_refresh"] == expected


def test_given_expired_token_when_check_then_token_is_refreshed_and_saved_without_check_overrides(requests_mock, capsys):
    """`check` runs with `config_overrides: {max_waiting_time: 1}`. The refreshed tokens must be
    saved, and the override must not be saved with them."""
    branches = mock_repository(requests_mock)
    refresh = mock_refresh(requests_mock)
    config = {**oauth_config(), "max_waiting_time": 30}
    source = make_source(config=config)
    capsys.readouterr()

    status = source.check(logging.getLogger("airbyte"), config)

    assert status.status == Status.SUCCEEDED, status.message
    assert refresh.call_count == 1
    assert parse_qs(refresh.last_request.text) == {
        "grant_type": ["refresh_token"],
        "client_id": ["client-id"],
        "client_secret": ["client-secret"],
        "refresh_token": ["stored-refresh-token"],
    }
    assert refresh.last_request.headers["Accept"] == "application/json"
    assert branches.last_request.headers["Authorization"] == "Bearer new-access-token"

    (emitted,) = emitted_configs(capsys)
    assert emitted["credentials"]["access_token"] == "new-access-token"
    assert emitted["credentials"]["refresh_token"] == "new-refresh-token"
    assert emitted["credentials"]["token_expiry_date"] > "2026"
    assert emitted["credentials"]["client_id"] == "client-id"
    assert emitted["credentials"]["client_secret"] == "client-secret"
    assert emitted["max_waiting_time"] == 30
    assert emitted["repositories"] == ["org/repo"]


def test_given_expired_token_when_read_then_token_is_refreshed_once_and_saved(requests_mock, capsys):
    branches = mock_repository(requests_mock)
    refresh = mock_refresh(requests_mock)
    source = make_source(config=oauth_config())
    capsys.readouterr()

    records = read_branches(source)

    assert [record["name"] for record in records] == ["main"]
    assert refresh.call_count == 1
    assert {request.headers["Authorization"] for request in requests_mock.request_history if request.method == "GET"} == {
        "Bearer new-access-token"
    }
    assert branches.called
    (emitted,) = emitted_configs(capsys)
    assert emitted["credentials"]["refresh_token"] == "new-refresh-token"


def test_given_valid_token_when_read_then_stored_token_is_used_and_nothing_is_refreshed(requests_mock, capsys):
    branches = mock_repository(requests_mock)
    refresh = mock_refresh(requests_mock)
    source = make_source(config=oauth_config(token_expiry_date=NOT_EXPIRED))
    capsys.readouterr()

    read_branches(source)

    assert refresh.call_count == 0
    assert branches.last_request.headers["Authorization"] == "Bearer stored-access-token"
    assert emitted_configs(capsys) == []


def test_given_oauth_config_without_refresh_token_when_read_then_stored_token_is_sent_as_before(
    requests_mock, rate_limit_mock_response, capsys
):
    """An OAuth app with expiring tokens turned off returns no refresh token. Such a source keeps
    the authenticator it always had: `token` scheme, quota tracking, no refresh request."""
    branches = mock_repository(requests_mock)
    refresh = mock_refresh(requests_mock)
    config = oauth_config()
    del config["credentials"]["refresh_token"], config["credentials"]["token_expiry_date"]
    source = make_source(config=config)
    capsys.readouterr()

    read_branches(source)

    assert refresh.call_count == 0
    assert branches.last_request.headers["Authorization"] == "token stored-access-token"
    assert emitted_configs(capsys) == []


@pytest.mark.parametrize("status_code", [200, 400, 401])
def test_given_rejected_refresh_token_when_read_then_config_error_and_nothing_is_saved(requests_mock, capsys, status_code):
    """GitHub reports a used or expired refresh token as `error: bad_refresh_token`. The stream
    has to stop with a config error that asks the user to authenticate again."""
    branches = mock_repository(requests_mock)
    refresh = mock_refresh(
        requests_mock,
        status_code=status_code,
        json={
            "error": "bad_refresh_token",
            "error_description": "The refresh token passed is incorrect or expired.",
            "error_uri": "https://docs.github.com/apps/managing-oauth-apps/troubleshooting-oauth-app-access-token-request-errors/",
        },
    )
    source = make_source(config=oauth_config())
    capsys.readouterr()

    with pytest.raises(AirbyteTracedException) as error:
        read_branches(source)

    assert error.value.failure_type == FailureType.config_error
    assert refresh.call_count == 1
    assert not branches.called
    assert emitted_configs(capsys) == []


@pytest.mark.parametrize("status_code", [200, 400, 401])
def test_given_wrong_client_credentials_when_read_then_config_error_that_names_the_oauth_app(requests_mock, capsys, status_code):
    """GitHub answers a wrong client ID or secret with HTTP 200 and `error: incorrect_client_credentials`.
    Signing in again does not fix it, so the message has to point at the OAuth app credentials."""
    branches = mock_repository(requests_mock)
    refresh = mock_refresh(
        requests_mock,
        status_code=status_code,
        json={
            "error": "incorrect_client_credentials",
            "error_description": "The client_id and/or client_secret passed are incorrect.",
            "error_uri": "https://docs.github.com/apps/managing-oauth-apps/troubleshooting-oauth-app-access-token-request-errors/#incorrect-client-credentials",
        },
    )
    source = make_source(config=oauth_config())
    capsys.readouterr()

    with pytest.raises(AirbyteTracedException) as error:
        read_branches(source)

    assert error.value.failure_type == FailureType.config_error
    assert "Check the OAuth app credentials" in error.value.message
    assert refresh.call_count == 1
    assert not branches.called
    assert emitted_configs(capsys) == []


def test_given_rejected_refresh_token_when_check_then_check_fails(requests_mock, capsys):
    mock_repository(requests_mock)
    mock_refresh(requests_mock, json={"error": "bad_refresh_token", "error_description": "The refresh token passed is incorrect or expired."})
    config = oauth_config()
    source = make_source(config=config)
    capsys.readouterr()

    status = source.check(logging.getLogger("airbyte"), config)

    assert status.status == Status.FAILED
    assert emitted_configs(capsys) == []


def test_given_legacy_repository_string_when_token_is_refreshed_then_saved_config_keeps_the_list_form(requests_mock, capsys):
    """The saved config is the normalized one, so every value in it has to be JSON-serializable
    and the legacy `repository` key has to survive for a downgrade."""
    requests_mock.get("https://api.github.com/repos/org/repo", json={"full_name": "org/repo", "default_branch": "main"})
    requests_mock.get("https://api.github.com/repos/org/other", json={"full_name": "org/other", "default_branch": "main"})
    requests_mock.get(BRANCHES_URL, json=[{"name": "main", "commit": {"sha": "abc"}}])
    requests_mock.get("https://api.github.com/repos/org/other/branches", json=[])
    mock_refresh(requests_mock)
    config = oauth_config()
    del config["repositories"]
    config["repository"] = "org/repo org/other org/repo"
    config["branch"] = "org/repo/main"
    source = make_source(config=config)
    capsys.readouterr()

    read_branches(source)

    (emitted,) = emitted_configs(capsys)
    assert emitted["repositories"] == ["org/other", "org/repo"]
    assert emitted["repository"] == "org/repo org/other org/repo"
    assert emitted["branches"] == ["org/repo/main"]
    assert emitted["credentials"]["refresh_token"] == "new-refresh-token"


def test_given_empty_lists_next_to_legacy_strings_when_token_is_refreshed_then_saved_config_is_serializable(requests_mock, capsys):
    """An empty `repositories` or `branches` list next to its legacy string skips the config
    migration, and `ConfigNormalization` fills the list in. It must not fill in a set: the saved
    config is serialized to JSON."""
    mock_repository(requests_mock)
    mock_refresh(requests_mock)
    config = {**oauth_config(), "repositories": [], "repository": "org/repo org/repo", "branches": [], "branch": "org/repo/main"}
    source = make_source(config=config)
    capsys.readouterr()

    read_branches(source)

    (emitted,) = emitted_configs(capsys)
    assert emitted["repositories"] == ["org/repo"]
    assert emitted["branches"] == ["org/repo/main"]
    assert emitted["credentials"]["refresh_token"] == "new-refresh-token"


def test_given_no_token_expiry_date_when_read_then_token_is_refreshed_before_the_first_request(requests_mock, capsys):
    branches = mock_repository(requests_mock)
    refresh = mock_refresh(requests_mock)
    config = oauth_config()
    del config["credentials"]["token_expiry_date"]
    source = make_source(config=config)
    capsys.readouterr()

    read_branches(source)

    assert refresh.call_count == 1
    assert branches.last_request.headers["Authorization"] == "Bearer new-access-token"


def test_spec_declares_the_refresh_token_fields_as_hidden_and_optional():
    source = make_source()
    spec = source.spec(logging.getLogger("airbyte"))
    oauth_option = next(
        option
        for option in spec.connectionSpecification["properties"]["credentials"]["oneOf"]
        if option["properties"]["option_title"]["const"] == "OAuth Credentials"
    )

    assert oauth_option["required"] == ["access_token"]
    assert oauth_option["properties"]["refresh_token"]["airbyte_secret"] is True
    assert oauth_option["properties"]["refresh_token"]["airbyte_hidden"] is True
    assert oauth_option["properties"]["token_expiry_date"]["airbyte_hidden"] is True
    assert "oauth_token_refresh" not in spec.connectionSpecification["properties"]

    oauth_input = spec.advanced_auth.oauth_config_specification.oauth_connector_input_specification
    assert oauth_input.extract_output == ["access_token"]
    assert oauth_input.optional_extract_output == ["refresh_token", "expires_in"]
    output_properties = spec.advanced_auth.oauth_config_specification.complete_oauth_output_specification["properties"]
    assert output_properties["refresh_token"]["path_in_connector_config"] == ["credentials", "refresh_token"]
    assert output_properties["token_expiry_date"]["path_in_connector_config"] == ["credentials", "token_expiry_date"]
