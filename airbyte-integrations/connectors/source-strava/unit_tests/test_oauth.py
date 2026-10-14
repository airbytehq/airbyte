# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import yaml

from airbyte_cdk.models import Status
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.models.declarative_component_schema import OAuthAuthenticator
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now


MANIFEST = yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())
TOKEN_URL = "https://www.strava.com/oauth/token"


@pytest.fixture
def config():
    return {
        "client_id": "12345",
        "client_secret": "abcdef",
        "refresh_token": "abcdef123456",
        "athlete_id": 12345,
        "start_date": "2021-01-01T00:00:00Z",
    }


def authenticator(config):
    return ModelToComponentFactory().create_component(
        OAuthAuthenticator, MANIFEST["definitions"]["base_requester"]["authenticator"], config
    )


def token_response(access_token="first-access", refresh_token="first-refresh"):
    return {"access_token": access_token, "refresh_token": refresh_token, "expires_in": 21600, "expires_at": 1791352800}


def response(request, body, status=200):
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(body).encode()
    result.headers["Content-Type"] = "application/json"
    result.request = request
    result.url = request.url
    return result


def test_token_expiry_and_rotated_refresh_token_are_persisted(config, capsys):
    properties = MANIFEST["spec"]["connection_specification"]["properties"]
    assert properties["access_token"]["airbyte_secret"]
    assert properties["access_token"]["airbyte_hidden"]

    def refresh(request, **kwargs):
        assert request.url == TOKEN_URL
        return response(request, token_response())

    with patch("requests.Session.send", side_effect=refresh) as send:
        now = ab_datetime_now()
        auth = authenticator(config)
        assert auth.get_access_token() == "first-access"
        assert config["refresh_token"] == "first-refresh"
        assert config["access_token"] == "first-access"
        expiry = auth.get_token_expiry_date()
        assert timedelta(hours=6) <= expiry - now < timedelta(hours=6, seconds=10)
        assert '"CONTROL"' in capsys.readouterr().out

        assert not auth.token_has_expired()
        assert authenticator(config).get_access_token() == "first-access"
        assert send.call_count == 1

        with patch(
            "airbyte_cdk.sources.streams.http.requests_native_auth.oauth.ab_datetime_now", return_value=expiry + timedelta(seconds=1)
        ):
            assert auth.token_has_expired()
            send.side_effect = lambda request, **kwargs: response(request, token_response("second-access", "second-refresh"))
            assert auth.get_access_token() == "second-access"
            assert "refresh_token=first-refresh" in send.call_args.args[0].body
            assert config["refresh_token"] == "second-refresh"


@pytest.mark.parametrize("activity_status, expected", [(200, Status.SUCCEEDED), (401, Status.FAILED), (403, Status.FAILED)])
def test_check_validates_activity_permissions(config, activity_status, expected):
    def send(request, **kwargs):
        if request.url == TOKEN_URL:
            return response(request, token_response())
        if request.url == "https://www.strava.com/api/v3/athletes/12345/stats":
            return response(request, {"all_run_totals": {"count": 0}})
        assert request.url.startswith("https://www.strava.com/api/v3/athlete/activities?")
        body = (
            []
            if activity_status == 200
            else {
                "message": "Authorization Error",
                "errors": [{"resource": "AccessToken", "field": "activity:read_permission", "code": "missing"}],
            }
        )
        return response(request, body, activity_status)

    with patch("requests.Session.send", side_effect=send) as mock_send:
        source = ConcurrentDeclarativeSource(source_config=MANIFEST, config=config)
        result = source.check(logging.getLogger("test"), config)
        assert result.status == expected
        urls = [call.args[0].url for call in mock_send.call_args_list]
        assert any("/athlete/activities?" in url for url in urls)
        assert urls.count(TOKEN_URL) == 1
