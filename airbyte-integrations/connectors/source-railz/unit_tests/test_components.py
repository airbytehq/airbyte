#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from datetime import datetime, timezone
from unittest.mock import patch

import requests_mock


def test_get_tokens(components_module):
    url = "https://auth.railz.ai/getAccess"
    responses = [
        {"access_token": "access_token1"},
        {"access_token": "access_token2"},
    ]
    requests_mock.get(url, json=lambda request, context: responses.pop(0))

    timestamps = [
        datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).timestamp(),
        datetime(2023, 1, 1, 12, 30, 0, tzinfo=timezone.utc).timestamp(),
        datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc).timestamp(),
    ]

    ShortLivedTokenAuthenticator = components_module.ShortLivedTokenAuthenticator
    authenticator = ShortLivedTokenAuthenticator(
        client_id="client_id",
        secret_key="secret_key",
        url=url,
        token_key="access_token",
        lifetime="PT3600S",
        config={},
        parameters={},
    )

    # Mock time.time() to return our predefined timestamps
    with patch("time.time", side_effect=timestamps):
        assert authenticator.token == "Bearer access_token1"
        assert authenticator.token == "Bearer access_token1"
        assert authenticator.token == "Bearer access_token2"
