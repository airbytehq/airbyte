#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import pytest


@pytest.fixture(params=["gitlab.com", "http://gitlab.com", "https://gitlab.com"])
def config(request):
    return {
        "start_date": "2021-01-01T00:00:00Z",
        "api_url": request.param,
        "credentials": {"auth_type": "access_token", "access_token": "token"},
    }


@pytest.fixture
def oauth_config():
    return {
        "api_url": "gitlab.com",
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "access_token": "access_token",
            "token_expiry_date": "2023-01-01T00:00:00Z",
            "refresh_token": "refresh_token",
        },
        "start_date": "2021-01-01T00:00:00Z",
    }


@pytest.fixture
def config_with_project_groups():
    return {
        "start_date": "2021-01-01T00:00:00Z",
        "api_url": "https://gitlab.com",
        "credentials": {"auth_type": "access_token", "access_token": "token"},
        "groups_list": ["g1"],
        "projects_list": ["p1"],
    }
