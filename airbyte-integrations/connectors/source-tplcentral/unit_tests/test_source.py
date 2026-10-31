#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

from pytest import fixture
from source_tplcentral.source import SourceTplcentral


@fixture
def config():
    return {
        "url_base": "https://secure-wms.com/",
        "client_id": "xxx",
        "client_secret": "yyy",
        "user_login_id": 123,
        "tpl_key": "{00000000-0000-0000-0000-000000000000}",
        "customer_id": 4,
        "facility_id": 5,
        "start_date": "2021-10-01",
    }


def test_check_connection(requests_mock, config):
    source = SourceTplcentral()
    logger_mock = MagicMock()
    requests_mock.post(
        f"{config['url_base']}AuthServer/api/Token",
        json={
            "access_token": "the_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": None,
            "scope": None,
        },
    )
    assert source.check_connection(logger_mock, config) == (True, None)


def test_authenticator_fetches_client_credentials_token_once(requests_mock, config):
    token_endpoint = f"{config['url_base']}AuthServer/api/Token"
    requests_mock.post(
        token_endpoint,
        json={"access_token": "the_token", "token_type": "Bearer", "expires_in": 3600},
    )

    auth = SourceTplcentral()._auth(config)

    assert auth.get_auth_header() == {"Authorization": "Bearer the_token"}
    assert auth.get_auth_header() == {"Authorization": "Bearer the_token"}
    assert requests_mock.call_count == 1
    request = requests_mock.request_history[0]
    assert json.loads(request.text) == {"grant_type": "client_credentials", "user_login_id": 123}
    assert request.headers["Authorization"] == "Basic eHh4Onl5eQ=="
    assert auth.token_has_expired() is False


def test_streams(config):
    source = SourceTplcentral()
    streams = source.streams(config)
    expected_streams_number = 6
    assert len(streams) == expected_streams_number
