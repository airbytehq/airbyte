#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams.http.auth import MultipleTokenAuthenticator
from source_github import SourceGithub


def test_single_token():
    authenticator = SourceGithub._get_authenticator("123")
    assert isinstance(authenticator, MultipleTokenAuthenticator)
    assert ["123"] == authenticator._tokens


def test_multiple_tokens():
    authenticator = SourceGithub._get_authenticator("123, 456")
    assert isinstance(authenticator, MultipleTokenAuthenticator)
    assert ["123", "456"] == authenticator._tokens
