#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(params=["gitlab.com", "https://gitlab.com", "https://gitlab.com/api/v4"])
def config(request):
    return {
        "start_date": "2021-01-01T00:00:00Z",
        "api_url": request.param,
        "credentials": {
            "auth_type": "access_token",
            "access_token": "token"
        }
    }


@pytest.fixture(autouse=True)
def disable_cache(mocker):
    mocker.patch(
        "source_gitlab.streams.Projects.use_cache",
        new_callable=mocker.PropertyMock,
        return_value=False
    )
    mocker.patch(
        "source_gitlab.streams.Groups.use_cache",
        new_callable=mocker.PropertyMock,
        return_value=False
    )
