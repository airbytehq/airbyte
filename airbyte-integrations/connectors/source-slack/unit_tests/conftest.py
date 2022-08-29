#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
from typing import MutableMapping

import pytest


@pytest.fixture(autouse=True)
def conversations_list(requests_mock):
    return requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=100&types=public_channel",
        json={
            "channels": [
                {"name": "advice-data-architecture", "id": 1},
                {"name": "advice-data-orchestration", "id": 2},
                {"name": "airbyte-for-beginners", "id": 3},
                {"name": "good-reads", "id": 4},
            ]
        },
    )


@pytest.fixture(autouse=True)
def join_channels(requests_mock):
    return requests_mock.register_uri("POST", "https://slack.com/api/conversations.join")


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
        (_legacy_token_config(), True),
        (_invalid_config(), False),
    ),
)
