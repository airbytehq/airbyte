#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from source_qonto.auth import QontoApiKeyAuthenticator


def test_authenticator():
    mocked_config = {"organization_slug": "test_slug", "secret_key": "test_key"}
    authenticator = QontoApiKeyAuthenticator(**mocked_config)
    expected_authenticator = {"Authorization": "test_slug:test_key"}
    assert authenticator.get_auth_header() == expected_authenticator
