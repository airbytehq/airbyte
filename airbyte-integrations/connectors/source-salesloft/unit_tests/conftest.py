#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture
def config():
    return {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
            "access_token": "access_token",
            "token_expiry_date": "2222-02-02T00:00:00Z",
        },
        "start_date": "2020-01-01T00:00:00.000Z",
    }
