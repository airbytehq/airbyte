#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest

from source_opsgenie import SourceOpsgenie

from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator


class AuthenticatorTestCase(unittest.TestCase):
    def test_token(self):
        authenticator = SourceOpsgenie.get_authenticator({"api_token": "123"})
        assert isinstance(authenticator, TokenAuthenticator)
        assert authenticator.token == "GenieKey 123"
        assert authenticator.auth_header == "Authorization"
