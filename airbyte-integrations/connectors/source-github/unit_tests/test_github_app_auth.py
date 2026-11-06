#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""GitHub App authentication: rotating installation tokens through `RateLimitedMultipleTokenAuthenticator`.

Each configured installation logs in on first use (`POST /app/installations/{id}/access_tokens`,
signed with a JWT from the app's private key) and its installation token is used as a Bearer
token. The installations then rotate exactly like multiple personal access tokens, with quota
tracked per installation id.
"""

import logging
from datetime import timedelta

import jwt
import pytest
import requests
from components import ConfigNormalization
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from freezegun import freeze_time

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    FailureType,
    SyncMode,
    Type,
)
from airbyte_cdk.sources.declarative.auth.rate_limited_multiple_token import (
    RateLimitedMultipleTokenAuthenticator,
)
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .utils import get_authenticator, make_source


_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PRIVATE_KEY_PEM = _PRIVATE_KEY.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()
).decode()
_PUBLIC_KEY = _PRIVATE_KEY.public_key()

_INSTALLATIONS = [("1001", "111"), ("1001", "222")]


def _app_config(installations=_INSTALLATIONS, **overrides):
    return {
        "credentials": {
            "option_title": "GitHub App Credentials",
            "installations": [
                {"app_id": app_id, "installation_id": installation_id, "private_key": _PRIVATE_KEY_PEM}
                for app_id, installation_id in installations
            ],
        },
        "repositories": ["org/repo"],
        **overrides,
    }


def _access_tokens_url(installation_id):
    return f"https://api.github.com/app/installations/{installation_id}/access_tokens"


def _mock_logins(requests_mock, suffix=""):
    """One installation token per installation: `inst-<installation id><suffix>`."""
    return {
        installation_id: requests_mock.post(
            _access_tokens_url(installation_id),
            json={"token": f"inst-{installation_id}{suffix}", "expires_at": "2099-01-01T00:00:00Z"},
            status_code=201,
        )
        for _, installation_id in _INSTALLATIONS
    }


def _catalog(*stream_names):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
            for stream_name in stream_names
        ]
    )


def _read(config, *stream_names):
    catalog = _catalog(*stream_names)
    source = make_source(config=dict(config), catalog=catalog, state=[])
    messages, error = [], None
    try:
        for message in source.read(logging.getLogger("airbyte"), dict(config), catalog, []):
            messages.append(message)
    except Exception as exc:  # noqa: BLE001 - the assertions inspect the failure
        error = exc
    return messages, error


def _authorization_headers(requests_mock, path):
    return {request.headers["Authorization"] for request in requests_mock.request_history if request.path == path}


def test_spec_offers_github_app_option():
    spec = make_source().spec(logging.getLogger("airbyte"))
    options = spec.connectionSpecification["properties"]["credentials"]["oneOf"]
    app_option = next(option for option in options if option["title"] == "GitHub App")

    assert app_option["properties"]["option_title"]["const"] == "GitHub App Credentials"
    installation = app_option["properties"]["installations"]["items"]
    assert installation["required"] == ["app_id", "installation_id", "private_key"]
    assert installation["properties"]["private_key"]["airbyte_secret"] is True


def test_selects_installation_authenticator(rate_limit_mock_response):
    config = _app_config()
    authenticator = get_authenticator(make_source(config=config), config)

    assert isinstance(authenticator, RateLimitedMultipleTokenAuthenticator)
    assert list(authenticator._tokens) == ["111", "222"]


def test_read_signs_requests_with_installation_tokens_and_logs_in_once(rate_limit_mock_response, requests_mock):
    """Two streams, two installations: one login per installation for the whole read, every
    request signed with one of the installation tokens, and quota seeded for each of them."""
    logins = _mock_logins(requests_mock)
    requests_mock.get("https://api.github.com/repos/org/repo", json={"full_name": "org/repo", "organization": {"login": "org"}})
    requests_mock.get("https://api.github.com/repos/org/repo/assignees", json=[{"id": 1}, {"id": 2}])
    requests_mock.get("https://api.github.com/repos/org/repo/branches", json=[{"name": "main"}])

    messages, error = _read(_app_config(), "assignees", "branches")

    assert error is None
    records = [message.record for message in messages if message.type == Type.RECORD]
    assert sorted(record.stream for record in records) == ["assignees", "assignees", "branches"]
    assert {installation_id: login.call_count for installation_id, login in logins.items()} == {"111": 1, "222": 1}
    installation_tokens = {"Bearer inst-111", "Bearer inst-222"}
    assert _authorization_headers(requests_mock, "/rate_limit") == installation_tokens
    for path in ("/repos/org/repo/assignees", "/repos/org/repo/branches"):
        assert _authorization_headers(requests_mock, path) <= installation_tokens


def test_login_is_signed_with_app_jwt(rate_limit_mock_response, requests_mock):
    logins = _mock_logins(requests_mock)
    config = _app_config()
    authenticator = get_authenticator(make_source(config=config), config)

    authenticator(requests.Request("GET", "https://api.github.com/repos/org/repo").prepare())

    for login in logins.values():
        scheme, token = login.last_request.headers["Authorization"].split(" ")
        claims = jwt.decode(token, _PUBLIC_KEY, algorithms=["RS256"])
        assert scheme == "Bearer"
        assert jwt.get_unverified_header(token)["alg"] == "RS256"
        assert claims["iss"] == "1001"
        # GitHub rejects an app JWT whose lifetime exceeds 10 minutes; `iat` is backdated for clock drift.
        assert claims["exp"] - claims["iat"] <= 600
        assert claims["iat"] <= claims["exp"] - 540 - 60
        assert login.last_request.headers["Accept"] == "application/vnd.github+json"


def test_installation_token_is_refreshed_before_it_expires(rate_limit_mock_response, requests_mock):
    config = _app_config(installations=[("1001", "111")])
    login = requests_mock.post(
        _access_tokens_url("111"),
        [{"json": {"token": "inst-111-first"}, "status_code": 201}, {"json": {"token": "inst-111-second"}, "status_code": 201}],
    )
    request = requests.Request("GET", "https://api.github.com/repos/org/repo").prepare()

    with freeze_time(ab_datetime_now()) as frozen:
        authenticator = get_authenticator(make_source(config=config), config)
        assert authenticator(request).headers["Authorization"] == "Bearer inst-111-first"
        frozen.tick(timedelta(minutes=30))
        assert authenticator(request).headers["Authorization"] == "Bearer inst-111-first"
        frozen.tick(timedelta(minutes=26))
        assert authenticator(request).headers["Authorization"] == "Bearer inst-111-second"

    assert login.call_count == 2


def test_api_url_applies_to_installation_login(requests_mock):
    """GitHub Enterprise Server: the login goes to the configured API URL, not api.github.com."""
    api_url = "https://github.company.org/api/v3"
    requests_mock.get(f"{api_url}/rate_limit", status_code=404, json={"message": "Rate limiting is not enabled."})
    login = requests_mock.post(f"{api_url}/app/installations/111/access_tokens", json={"token": "inst-111"}, status_code=201)
    config = _app_config(installations=[("1001", "111")], api_url=api_url)

    authenticator = get_authenticator(make_source(config=config), config)
    signed = authenticator(requests.Request("GET", f"{api_url}/repos/org/repo").prepare())

    assert login.call_count == 1
    assert signed.headers["Authorization"] == "Bearer inst-111"


@pytest.mark.parametrize("status_code", [401, 403, 404])
def test_rejected_login_is_config_error(status_code, rate_limit_mock_response, requests_mock):
    requests_mock.post(_access_tokens_url("111"), status_code=status_code, json={"message": "Not Found"})
    config = _app_config(installations=[("1001", "111")])
    authenticator = get_authenticator(make_source(config=config), config)

    with pytest.raises(AirbyteTracedException) as error:
        authenticator(requests.Request("GET", "https://api.github.com/repos/org/repo").prepare())

    assert error.value.failure_type == FailureType.config_error
    assert "111" in error.value.message
    assert "installation access token" in error.value.message


@pytest.mark.parametrize(
    "config",
    [
        pytest.param({"access_token": "root-token"}, id="root_access_token_without_credentials"),
        pytest.param({"credentials": {"personal_access_token": "pat-token"}}, id="credentials_without_option_title"),
    ],
)
def test_configs_without_option_title_keep_token_authentication(config):
    ConfigNormalization().transform(config)

    assert config["credentials"]["option_title"] == "PAT Credentials"


def test_option_title_is_not_overwritten():
    config = {"credentials": {"option_title": "OAuth Credentials", "access_token": "oauth-token"}}

    ConfigNormalization().transform(config)

    assert config["credentials"] == {"option_title": "OAuth Credentials", "access_token": "oauth-token"}
