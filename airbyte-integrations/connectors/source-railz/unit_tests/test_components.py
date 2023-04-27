#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from freezegun import freeze_time
from source_railz.components import ShortLivedTokenAuthenticator


def test_get_tokens(requests_mock):
    url = "https://auth.railz.ai/getAccess"

    responses = [
        {"access_token": "access_token1"},
        {"access_token": "access_token2"},
    ]
    requests_mock.get(url, json=lambda request, context: responses.pop(0))

    authenticator = ShortLivedTokenAuthenticator(
        client_id="client_id",
        secret_key="secret_key",
        url=url,
        token_key="access_token",
        lifetime="PT3600S",
        config={},
        parameters={},
    )

    with freeze_time("2023-01-01 12:00:00"):
        assert authenticator.token == "Bearer access_token1"
    with freeze_time("2023-01-01 12:30:00"):
        assert authenticator.token == "Bearer access_token1"
    with freeze_time("2023-01-01 13:00:00"):
        assert authenticator.token == "Bearer access_token2"
