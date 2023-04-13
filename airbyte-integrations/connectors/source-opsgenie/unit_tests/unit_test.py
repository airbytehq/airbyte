#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import unittest

from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator
from source_opsgenie import SourceOpsgenie


class AuthenticatorTestCase(unittest.TestCase):
    def test_token(self):
        authenticator = SourceOpsgenie.get_authenticator({"api_token": "123"})
        self.assertIsInstance(authenticator, TokenAuthenticator)
        self.assertEqual("GenieKey 123", authenticator.token)
        self.assertEqual("Authorization", authenticator.auth_header)
