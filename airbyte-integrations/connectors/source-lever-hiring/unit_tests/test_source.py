#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from source_lever_hiring.source import SourceLeverHiring


@pytest.mark.parametrize(
    ("response", "url", "payload", "test_config"),
    [
        (
            responses.POST,
            "https://sandbox-lever.auth0.com/oauth/token",
            {"access_token": "test_access_token", "expires_in": 3600},
            {
                "credentials": {
                    "auth_type": "Client",
                    "client_id": "test_client_id",
                    "client_secret": "test_client_secret",
                    "refresh_token": "test_refresh_token",
                    "access_token": "test_access_token",
                    "expires_in": 3600,
                },
                "environment": "Sandbox",
                "start_date": "2021-05-07T00:00:00Z",
            },
        ),
        (
            None,
            None,
            None,
            {
                "credentials": {
                    "auth_type": "Api Key",
                    "api_key": "test_api_key",
                },
                "environment": "Sandbox",
                "start_date": "2021-05-07T00:00:00Z",
            },
        ),
    ],
)
@responses.activate
def test_source(response, url, payload, test_config):
    if response:
        responses.add(response, url, json=payload)
    source = SourceLeverHiring()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)
    assert len(source.streams(test_config)) == 7
