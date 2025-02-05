#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch
from datetime import datetime, timedelta

def test_get_tokens(components_module, requests_mock):
    url = "https://auth.railz.ai/getAccess"

    responses = [
        {"access_token": "access_token1"},
        {"access_token": "access_token2"},
    ]
    requests_mock.get(url, json=lambda request, context: responses.pop(0))

    authenticator = components_module.ShortLivedTokenAuthenticator(
        client_id="client_id",
        secret_key="secret_key",
        url=url,
        token_key="access_token",
        lifetime="PT3600S",
        config={},
        parameters={},
    )

    start_time = datetime(2023, 1, 1, 12, 0, 0)

    with patch("components_module.ShortLivedTokenAuthenticator._current_time", return_value=start_time):
        assert authenticator.token == "Bearer access_token1"

    with patch("components_module.ShortLivedTokenAuthenticator._current_time", return_value=start_time + timedelta(minutes=30)):
        assert authenticator.token == "Bearer access_token1"

    with patch("components_module.ShortLivedTokenAuthenticator._current_time", return_value=start_time + timedelta(hours=1)):
        assert authenticator.token == "Bearer access_token2"
