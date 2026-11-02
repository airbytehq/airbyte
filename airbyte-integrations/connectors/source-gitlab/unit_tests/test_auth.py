#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read

from .conftest import BASE_CONFIG, get_source


GROUPS_LIST_URL = "https://gitlab.com/api/v4/groups?per_page=50"
GROUP_URL = "https://gitlab.com/api/v4/groups/g1?per_page=50"
TOKEN_URL = "https://gitlab.com/oauth/token"

INITIAL_ACCESS_TOKEN = "initial_access_token"
NEW_ACCESS_TOKEN = "new_access_token"
INVALID_TOKEN_BODY = {
    "error": "invalid_token",
    "error_description": "Token is expired. You can either do re-authorization or token refresh.",
}
UNAUTHORIZED_BODY = {"message": "401 Unauthorized"}
CREDENTIALS_ERROR_MESSAGE = "GitLab rejected the credentials"


def _oauth_config(token_expiry_date: str = "2099-01-01T00:00:00Z", api_url: str = None):
    config = BASE_CONFIG | {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "access_token": INITIAL_ACCESS_TOKEN,
            "token_expiry_date": token_expiry_date,
            "refresh_token": "refresh_token",
        },
    }
    if api_url:
        config["api_url"] = api_url
    return config


def _token_response():
    return {
        "access_token": NEW_ACCESS_TOKEN,
        "token_type": "Bearer",
        "expires_in": 7200,
        "refresh_token": "new_refresh_token",
        "created_at": 1735689600,
    }


def _read_groups(config):
    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream("groups", SyncMode.full_refresh).build()
    return read(source, config, catalog, expecting_exception=True)


def _mock_group_detail(requests_mock):
    requests_mock.get(GROUP_URL, json={"id": "g1", "name": "group 1", "projects": []})


def test_oauth_invalid_token_refreshes_and_retries_request(requests_mock, mocker):
    mocker.patch("time.sleep")
    token_matcher = requests_mock.post(TOKEN_URL, json=_token_response())
    sent_authorization_headers = []

    def _groups_response(request, context):
        sent_authorization_headers.append(request.headers["Authorization"])
        if len(sent_authorization_headers) == 1:
            context.status_code = 401
            return INVALID_TOKEN_BODY
        return [{"id": "g1"}]

    groups_matcher = requests_mock.get(GROUPS_LIST_URL, json=_groups_response)
    _mock_group_detail(requests_mock)

    output = _read_groups(_oauth_config())

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == ["g1"]
    assert token_matcher.call_count == 1
    assert groups_matcher.call_count == 2
    assert sent_authorization_headers == [f"Bearer {INITIAL_ACCESS_TOKEN}", f"Bearer {NEW_ACCESS_TOKEN}"]


def test_oauth_invalid_token_after_refresh_fails_as_config_error(requests_mock, mocker):
    mocker.patch("time.sleep")
    token_matcher = requests_mock.post(TOKEN_URL, json=_token_response())
    groups_matcher = requests_mock.get(GROUPS_LIST_URL, status_code=401, json=INVALID_TOKEN_BODY)

    output = _read_groups(_oauth_config())

    assert token_matcher.call_count == 1
    assert groups_matcher.call_count == 2
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert "Refreshed OAuth access token is rejected by the API." in output.errors[0].trace.error.message
    assert not output.records


def test_oauth_unauthorized_without_invalid_token_fails_fast_as_config_error(requests_mock, mocker):
    mocker.patch("time.sleep")
    token_matcher = requests_mock.post(TOKEN_URL, json=_token_response())
    groups_matcher = requests_mock.get(GROUPS_LIST_URL, status_code=401, json=UNAUTHORIZED_BODY)

    output = _read_groups(_oauth_config())

    assert token_matcher.call_count == 0
    assert groups_matcher.call_count == 1
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert CREDENTIALS_ERROR_MESSAGE in output.errors[0].trace.error.message


@pytest.mark.parametrize("body", (UNAUTHORIZED_BODY, INVALID_TOKEN_BODY), ids=("unauthorized", "invalid_token"))
def test_private_token_unauthorized_fails_fast_as_config_error(requests_mock, mocker, body):
    mocker.patch("time.sleep")
    groups_matcher = requests_mock.get(GROUPS_LIST_URL, status_code=401, json=body)

    output = _read_groups(BASE_CONFIG)

    assert groups_matcher.call_count == 1
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert CREDENTIALS_ERROR_MESSAGE in output.errors[0].trace.error.message


@pytest.mark.parametrize(
    ("api_url", "expected_token_url", "expected_api_url"),
    (
        (None, "https://gitlab.com/oauth/token", "https://gitlab.com/api/v4/groups?per_page=50"),
        ("gitlab.com", "https://gitlab.com/oauth/token", "https://gitlab.com/api/v4/groups?per_page=50"),
        ("https://gitlab.com", "https://gitlab.com/oauth/token", "https://gitlab.com/api/v4/groups?per_page=50"),
        (
            "https://gitlab.company.org",
            "https://gitlab.company.org/oauth/token",
            "https://gitlab.company.org/api/v4/groups?per_page=50",
        ),
        (
            "http://gitlab.internal.org",
            "http://gitlab.internal.org/oauth/token",
            "http://gitlab.internal.org/api/v4/groups?per_page=50",
        ),
    ),
)
def test_token_refresh_endpoint_uses_api_url_scheme_and_host(requests_mock, mocker, api_url, expected_token_url, expected_api_url):
    mocker.patch("os.environ", {"DEPLOYMENT_MODE": "OSS"})
    token_matcher = requests_mock.post(expected_token_url, json=_token_response())
    groups_matcher = requests_mock.get(expected_api_url, json=[])

    output = _read_groups(_oauth_config(token_expiry_date="2020-01-01T00:00:00Z", api_url=api_url))

    assert not output.errors
    assert token_matcher.call_count == 1
    assert groups_matcher.call_count == 1
    assert groups_matcher.request_history[0].headers["Authorization"] == f"Bearer {NEW_ACCESS_TOKEN}"
