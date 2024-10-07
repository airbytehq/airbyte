#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.streams import Stream
from source_gitlab.source import SourceGitlab

BASE_CONFIG = {
    "start_date": "2021-01-01T00:00:00Z",
    "api_url": "gitlab.com",
    "credentials": {"auth_type": "access_token", "access_token": "token"},
}
GROUPS_LIST_URL = "https://gitlab.com/api/v4/groups?per_page=50"


@pytest.fixture(params=["gitlab.com", "http://gitlab.com", "https://gitlab.com"])
def config(request):
    return BASE_CONFIG | {"api_url": request.param}


@pytest.fixture
def oauth_config():
    return BASE_CONFIG | {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "access_token": "access_token",
            "token_expiry_date": "2023-01-01T00:00:00Z",
            "refresh_token": "refresh_token",
        },
    }


@pytest.fixture
def config_with_project_groups():
    return BASE_CONFIG | {"groups_list": ["g1"], "projects_list": ["p1"]}


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceGitlab()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]
