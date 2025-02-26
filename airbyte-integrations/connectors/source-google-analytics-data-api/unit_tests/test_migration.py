#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi
from source_google_analytics_data_api.config_migrations import MigratePropertyID

from airbyte_cdk.entrypoint import AirbyteEntrypoint


@patch.object(SourceGoogleAnalyticsDataApi, "read_config")
@patch.object(SourceGoogleAnalyticsDataApi, "write_config")
@patch.object(AirbyteEntrypoint, "extract_config")
def test_migration(ab_entrypoint_extract_config_mock, source_write_config_mock, source_read_config_mock):
    source = SourceGoogleAnalyticsDataApi()

    source_read_config_mock.return_value = {
        "credentials": {"auth_type": "Service", "credentials_json": "<credentials string ...>"},
        "custom_reports": "<custom reports out of current test>",
        "date_ranges_start_date": "2023-09-01",
        "window_in_days": 30,
        "property_id": "111111111",
    }
    ab_entrypoint_extract_config_mock.return_value = "/path/to/config.json"

    def check_migrated_value(new_config, path):
        assert path == "/path/to/config.json"
        assert "property_id" not in new_config
        assert "property_ids" in new_config
        assert "111111111" in new_config["property_ids"]
        assert len(new_config["property_ids"]) == 1

    source_write_config_mock.side_effect = check_migrated_value

    MigratePropertyID.migrate(["--config", "/path/to/config.json"], source)
