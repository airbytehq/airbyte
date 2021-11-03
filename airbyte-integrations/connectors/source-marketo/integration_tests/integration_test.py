#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
import json
from typing import Mapping, Any

from airbyte_cdk import AirbyteLogger
from source_marketo.source import SourceMarketo
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit

CONFIG_FILE = "secrets/config.json"
LOGGER = AirbyteLogger()


class TestIntegrationMarketo:
    @staticmethod
    def get_config_file(config_path: str) -> Mapping[str, Any]:
        with open(config_path, "r") as f:
            return json.loads(f.read())

    def test_window_in_days_maximum_value(self):
        config_file = self.get_config_file(CONFIG_FILE)
        config_file["window_in_days"] = 40  # Updated window_in_days to greater value than maximum (30 days)

        with pytest.raises(Exception) as validation_error:
            check_config_against_spec_or_exit(config_file, SourceMarketo().spec(LOGGER), LOGGER)

        expected_error_message = "Config validation error: 40 is greater than the maximum"
        assert expected_error_message in str(validation_error.value)
