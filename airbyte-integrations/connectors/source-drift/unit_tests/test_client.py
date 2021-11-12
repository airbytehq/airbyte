#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from source_drift.client import AuthError, Client


def test__heal_check_with_wrong_token():
    client = Client(access_token="wrong_key")
    alive, error = client.health_check()

    assert not alive
    assert error == "(401, 'The access token is invalid or has expired')"


def test__users_with_wrong_token():
    client = Client(access_token="wrong_key")
    with pytest.raises(AuthError, match="(401, 'The access token is invalid or has expired')"):
        next(client.stream__users())
