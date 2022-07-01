#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import logging
import os
from pathlib import Path

import pytest

LOGGER = logging.getLogger("airbyte")

CONNECTOR_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(name="sample_config")
def sample_config_fixture():
    pth = os.path.join(CONNECTOR_DIR, "integration_tests", "sample_config.json")
    with open(pth, "r") as f:
        return json.load(f)


@pytest.fixture(name="invalid_config")
def invalid_config_fixture():
    pth = os.path.join(CONNECTOR_DIR, "integration_tests", "invalid_config.json")
    with open(pth, "r") as f:
        return json.load(f)
