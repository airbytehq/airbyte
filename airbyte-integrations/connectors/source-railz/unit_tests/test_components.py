#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch


def test_get_tokens(components_module):
    url = "https://auth.railz.ai/getAccess"
    responses = [
        {"access_token": "access_token1"},
        {"access_token": "access_token1"},
        {"access_token": "access_token2"},
    ]

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

    def mock_requests_get(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.json.return_value = responses[0]
        return mock_response

    # Mock requests.get and time.time
    for _ in range(3):
        with patch("requests.Session.get", side_effect=mock_requests_get), patch("time.time", return_value=timestamps.pop(0)):
            assert authenticator.token == f"Bearer {responses.pop(0)['access_token']}"
