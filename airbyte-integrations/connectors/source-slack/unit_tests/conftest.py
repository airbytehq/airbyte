#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import os
from typing import MutableMapping

import pytest

os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


@pytest.fixture(autouse=True)
def conversations_list(requests_mock):
    return requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=1000&types=public_channel",
        json={
            "channels": [
                {"id": "airbyte-for-beginners", "is_member": True},
                {"id": "good-reads", "is_member": True}]
        },
    )

def base_config() -> MutableMapping:
    return copy.deepcopy(
        {
            "start_date": "2021-07-22T20:00:00Z",
            "end_date": "2021-07-23T20:00:00Z",
            "lookback_window": 1,
            "join_channels": True,
            "channel_filter": ["airbyte-for-beginners", "good-reads"],
        }
    )


def _token_config() -> MutableMapping:
    config = base_config()
    config.update({"credentials": {"option_title": "API Token Credentials", "api_token": "api-token"}})
    return config


@pytest.fixture
def token_config() -> MutableMapping:
    return _token_config()


def _oauth_config() -> MutableMapping:
    config = base_config()
    config.update(
        {
            "credentials": {
                "option_title": "Default OAuth2.0 authorization",
                "client_id": "client.id",
                "client_secret": "client-secret",
                "access_token": "access-token",
            }
        }
    )
    return config


@pytest.fixture
def oauth_config() -> MutableMapping:
    return _oauth_config()


def _legacy_token_config() -> MutableMapping:
    config = base_config()
    config.update({"api_token": "api-token"})
    return config


@pytest.fixture
def legacy_token_config() -> MutableMapping:
    return _legacy_token_config()


def _invalid_config() -> MutableMapping:
    return base_config()


@pytest.fixture
def invalid_config() -> MutableMapping:
    return _invalid_config()


parametrized_configs = pytest.mark.parametrize(
    "config, is_valid",
    (
        (_token_config(), True),
        (_oauth_config(), True),
        (_invalid_config(), False),
    ),
)


@pytest.fixture
def joined_channel():
    return {"id": "C061EG9SL", "name": "general", "is_channel": True, "is_group": False, "is_im": False,
            "created": 1449252889,
            "creator": "U061F7AUR", "is_archived": False, "is_general": True, "unlinked": 0, "name_normalized": "general",
            "is_shared": False,
            "is_ext_shared": False, "is_org_shared": False, "pending_shared": [], "is_pending_ext_shared": False,
            "is_member": True, "is_private": False, "is_mpim": False,
            "topic": {"value": "Which widget do you worry about?", "creator": "", "last_set": 0},
            "purpose": {"value": "For widget discussion", "creator": "", "last_set": 0}, "previous_names": []}
