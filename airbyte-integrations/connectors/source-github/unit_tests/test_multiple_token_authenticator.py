#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import responses

from source_github import SourceGithub
from source_github.utils import MultipleTokenAuthenticatorWithRateLimiter

@responses.activate
def test_multiple_tokens(rate_limit_mock_response):
    authenticator = SourceGithub()._get_authenticator({"access_token": "token_1, token_2, token_3"})
    assert isinstance(authenticator, MultipleTokenAuthenticatorWithRateLimiter)
    assert ["token_1", "token_2", "token_3"] == list(authenticator._tokens)


