from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.sources.streams.http import HttpStream

from source_zendesk_talk import SourceZendeskTalk


@pytest.fixture
def patch_base_class(mocker):
    return {
        "config": {
            "oauth2.0": {
                "credentials": {
                    "credentials": "oauth2.0",
                    "access_token": "accesstoken"
                },
                "subdomain": "airbyte-subdomain",
                "start_date": "2021-04-01T00:00:00Z"
            },
            "api_token": {
                "credentials": {
                    "credentials": "api_token",
                    "api_token": "accesstoken",
                    "email": "email@example.com"
                },
                "subdomain": "airbyte-subdomain",
                "start_date": "2021-04-01T00:00:00Z"
            },
        }
    }

@pytest.mark.parametrize(
    ("auth_type", "airbyte_status"),
    [
        ("oauth2.0", AirbyteConnectionStatus(status=Status.SUCCEEDED)),
        ("api_token", AirbyteConnectionStatus(status=Status.SUCCEEDED)),
    ],
)
def test_check_connection(mocker, patch_base_class, auth_type, airbyte_status):
    source = SourceZendeskTalk()
    record = MagicMock()

    logger_mock, config_mock = MagicMock(), MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class["config"][auth_type].__getitem__

    mocker.patch.object(
        HttpStream,
        "read_records",
        return_value=[record]
    )
    assert source.check(logger_mock, config_mock) == airbyte_status


def test_streams(mocker, patch_base_class):
    source = SourceZendeskTalk()

    config_mock = MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class["config"]["oauth2.0"].__getitem__

    streams = source.streams(config_mock)
    expected_streams_number = 13
    assert len(streams) == expected_streams_number
