#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(params=["gitlab.com", "https://gitlab.com", "https://gitlab.com/api/v4"])
def config(request):
    return {
        "start_date": "2021-01-01T00:00:00Z",
        "api_url": request.param,
        "private_token": "secret_token"
    }
