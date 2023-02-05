#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture
def config(mocker):
    return {
        "start_date": "2021-01-01T00:00:00Z",
        "api_url": "gitlab.com",
        "credentials": {
            "auth_type": "access_token",
            "access_token": "token"
        }
    }
