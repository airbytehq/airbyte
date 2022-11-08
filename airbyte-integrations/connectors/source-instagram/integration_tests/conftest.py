#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog


@pytest.fixture(scope="session", name="config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        return json.load(config_file)


@pytest.fixture(scope="session", name="configured_catalog")
def configured_catalog_fixture():
    return ConfiguredAirbyteCatalog.parse_file("integration_tests/configured_catalog.json")
