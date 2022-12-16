#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture
def config(mocker):
    return {
        "start_date": "2021-01-01T00:00:00Z",
        "api_url": "gitlab.com",
        "private_token": "secret_token"
    }
