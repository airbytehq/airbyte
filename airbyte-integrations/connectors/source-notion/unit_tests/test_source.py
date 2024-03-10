#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_notion.source import SourceNotion

UNAUTHORIZED_ERROR_MESSAGE = "The provided API access token is invalid. Please double-check that you input the correct token and have granted the necessary permissions to your Notion integration."
RESTRICTED_RESOURCE_ERROR_MESSAGE = "The provided API access token does not have the correct permissions configured. Please double-check that you have granted all the necessary permissions to your Notion integration."
GENERIC_ERROR_MESSAGE = "Conflict occurred while saving. Please try again."
DEFAULT_ERROR_MESSAGE = "An unspecified error occurred while connecting to Notion. Please check your credentials and try again."

def test_streams(mocker):
    source = SourceNotion()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number

@pytest.mark.parametrize(
    "config, expected_return",
    [
        ({}, None),
        ({"start_date": "2021-01-01T00:00:00.000Z"}, None),
        ({"start_date": "2021-99-99T79:89:99.123Z"}, "The provided start date is not a valid date. Please check the format and try again."),
        ({"start_date": "2021-01-01T00:00:00.000"}, "Please check the format of the start date against the pattern descriptor."),
        ({"start_date": "2025-01-25T00:00:00.000Z"}, "The start date cannot be greater than the current date."),
    ],
)
def test_validate_start_date(config, expected_return):
    source = SourceNotion()
    result = source._validate_start_date(config)
    assert result == expected_return
