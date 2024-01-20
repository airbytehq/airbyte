#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_fastbill.components import CustomAuthenticator


def test_token_generation():

    config = {"username": "example@gmail.com", "api_key": "api_key"}
    authenticator = CustomAuthenticator(config=config, username="example@gmail.com", password="api_key", parameters=None)
    token = authenticator.token
    expected_token = "Basic ZXhhbXBsZUBnbWFpbC5jb206YXBpX2tleQ=="
    assert expected_token == token
