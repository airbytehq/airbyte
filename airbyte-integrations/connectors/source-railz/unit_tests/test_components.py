#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


def test_get_tokens(components_module, requests_mock, mocker):
    url = "https://auth.railz.ai/getAccess"
    responses = [
        {"access_token": "access_token1"},
        {"access_token": "access_token2"},
    ]
    requests_mock.get(url, json=lambda request, context: responses.pop(0))

    current_time = 1000.0
    mock_time = mocker.patch("time.time", return_value=current_time)

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

    token1 = authenticator.token
    assert token1 == "Bearer access_token1"
    assert authenticator._timestamp == current_time

    mock_time.return_value = current_time + 1800
    assert authenticator.token == "Bearer access_token1"

    mock_time.return_value = current_time + 3601
    assert authenticator.token == "Bearer access_token2"
