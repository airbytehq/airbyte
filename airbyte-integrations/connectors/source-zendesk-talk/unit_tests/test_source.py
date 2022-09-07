#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.sources.streams.http import HttpStream
from source_zendesk_talk import SourceZendeskTalk


@pytest.fixture
def patch_base_class_oauth20(mocker):
    return {
        "config": {
            "credentials": {"auth_type": "oauth2.0", "access_token": "accesstoken"},
            "subdomain": "airbyte-subdomain",
            "start_date": "2021-04-01T00:00:00Z",
        }
    }


@pytest.fixture
def patch_base_class_api_token(mocker):
    return {
        "config": {
            "credentials": {"auth_type": "api_token", "api_token": "accesstoken", "email": "email@example.com"},
            "subdomain": "airbyte-subdomain",
            "start_date": "2021-04-01T00:00:00Z",
        }
    }


def test_check_connection_oauth20(mocker, patch_base_class_oauth20):
    source = SourceZendeskTalk()

    logger_mock, config_mock = mocker.MagicMock(), mocker.MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class_oauth20["config"].__getitem__

    mocker.patch.object(HttpStream, "read_records", return_value=[mocker.MagicMock()])
    assert source.check(logger_mock, config_mock) == AirbyteConnectionStatus(status=Status.SUCCEEDED)


def test_check_connection_api_token(mocker, patch_base_class_api_token):
    source = SourceZendeskTalk()

    logger_mock, config_mock = mocker.MagicMock(), mocker.MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class_api_token["config"].__getitem__

    mocker.patch.object(HttpStream, "read_records", return_value=[mocker.MagicMock()])
    assert source.check(logger_mock, config_mock) == AirbyteConnectionStatus(status=Status.SUCCEEDED)


def test_streams(mocker, patch_base_class_oauth20):
    source = SourceZendeskTalk()

    config_mock = mocker.MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class_oauth20["config"].__getitem__

    all_streams = source.streams(config_mock)

    expected_streams_number = 13
    streams = filter(
        lambda s: s.__class__.__name__
        in [
            "AccountOverview",
            "Addresses",
            "AgentsActivity",
            "AgentsOverview",
            "CurrentQueueActivity",
            "Greetings",
            "GreetingCategories",
            "IVRMenus",
            "IVRRoutes",
            "IVRs",
            "PhoneNumbers",
        ],
        all_streams,
    )

    incremental_streams = filter(
        lambda s: s.__class__.__name__
        in [
            "Calls",
            "CallLegs",
        ],
        all_streams,
    )

    assert len(all_streams) == expected_streams_number

    for s in incremental_streams:
        assert s._start_date == pendulum.parse(patch_base_class_oauth20["config"]["start_date"])
        assert s._subdomain == "airbyte-subdomain"

    for s in streams:
        assert s._subdomain == "airbyte-subdomain"
