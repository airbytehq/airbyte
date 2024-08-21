#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

import pytest
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from source_sendgrid.config_migrations import MigrateToLowcodeConfig
from source_sendgrid.source import SourceSendgrid

# Test data for parametrized test
test_data = [
    ({"apikey": "secret_value1"}, {"apikey": "secret_value1", "api_key": "secret_value1", "start_date": "2009-08-01T00:00:00Z"}),
    # Test when only apikey is present
    ({"apikey": "secret_value1"}, {"apikey": "secret_value1", "api_key": "secret_value1", "start_date": "2009-08-01T00:00:00Z"}),
    # Test having a time
    (
        {"apikey": "secret_value2", "start_time": "2019-05-20T13:43:57Z"},
        {"apikey": "secret_value2", "start_time": "2019-05-20T13:43:57Z", "api_key": "secret_value2", "start_date": "2019-05-20T13:43:57Z"},
    ),
    # Really old format
    (
        {"apikey": "secret_value2", "start_time": "1558359837"},
        {"apikey": "secret_value2", "start_time": "1558359837", "api_key": "secret_value2", "start_date": "2019-05-20T13:43:57Z"},
    ),
    # Test when the time has milliseconds
    (
        {"apikey": "secret_value2", "start_time": "2019-05-20T13:43:57.000Z"},
        {
            "apikey": "secret_value2",
            "start_time": "2019-05-20T13:43:57.000Z",
            "api_key": "secret_value2",
            "start_date": "2019-05-20T13:43:57Z",
        },
    ),
    # Test when neither api_secret nor project_id are present
    ({"other_key": "value"}, {"other_key": "value"}),
    # test when other stuff is around
    (
        {"other_key": "value", "apikey": "secret_value3"},
        {"other_key": "value", "apikey": "secret_value3", "api_key": "secret_value3", "start_date": "2009-08-01T00:00:00Z"},
    ),
    # Test when it's already right
    (
        {"api_key": "secret_value2", "start_date": "2019-05-20T13:43:57Z"},
        {"api_key": "secret_value2", "start_date": "2019-05-20T13:43:57Z"},
    ),
]


@pytest.mark.parametrize("test_config, expected", test_data)
@patch.object(AirbyteEntrypoint, "extract_config")
@patch.object(SourceSendgrid, "write_config")
@patch.object(SourceSendgrid, "read_config")
def test_transform_config(source_read_config_mock, source_write_config_mock, ab_entrypoint_extract_config_mock, test_config, expected):
    source = SourceSendgrid()

    source_read_config_mock.return_value = test_config
    ab_entrypoint_extract_config_mock.return_value = "/path/to/config.json"

    def check_migrated_value(new_config, path):
        assert path == "/path/to/config.json"
        assert new_config == expected

    source_write_config_mock.side_effect = check_migrated_value
    MigrateToLowcodeConfig.migrate(["--config", "/path/to/config.json"], source)
