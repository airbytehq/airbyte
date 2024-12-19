#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

import pytest
from source_mixpanel.config_migrations import MigrateProjectId
from source_mixpanel.source import SourceMixpanel

from airbyte_cdk.entrypoint import AirbyteEntrypoint


# Test data for parametrized test
test_data = [
    # Test when only api_secret is present
    ({"api_secret": "secret_value1"}, {"credentials": {"api_secret": "secret_value1"}}),
    # Test when only project_id is present
    ({"project_id": "project_value1"}, {"credentials": {"project_id": "project_value1"}}),
    # Test when both api_secret and project_id are present
    (
        {"api_secret": "secret_value2", "project_id": "project_value2"},
        {"credentials": {"api_secret": "secret_value2", "project_id": "project_value2"}},
    ),
    # Test when neither api_secret nor project_id are present
    ({"other_key": "value"}, {"other_key": "value"}),
]


@pytest.mark.parametrize("test_config, expected", test_data)
@patch.object(AirbyteEntrypoint, "extract_config")
@patch.object(SourceMixpanel, "write_config")
@patch.object(SourceMixpanel, "read_config")
def test_transform_config(source_read_config_mock, source_write_config_mock, ab_entrypoint_extract_config_mock, test_config, expected):
    source = SourceMixpanel()

    source_read_config_mock.return_value = test_config
    ab_entrypoint_extract_config_mock.return_value = "/path/to/config.json"

    def check_migrated_value(new_config, path):
        assert path == "/path/to/config.json"
        assert new_config == expected

    source_write_config_mock.side_effect = check_migrated_value
    MigrateProjectId.migrate(["--config", "/path/to/config.json"], source)
