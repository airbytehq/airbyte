#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import pytest
from typing import Any, Mapping
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import Status
from destination_google_sheets.destination import DestinationGoogleSheets


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config_oauth.json", "r") as f:
        return json.loads(f.read())
    
def test_check_valid_config(config: Mapping):
    outcome = DestinationGoogleSheets().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED