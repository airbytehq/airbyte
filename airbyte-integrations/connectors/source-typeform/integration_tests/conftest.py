#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pendulum
import pytest


@pytest.fixture(scope="session", name="config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        config = json.load(config_file)
        today = pendulum.now(tz="UTC")
        start_date = today.subtract(years=2)
        config["start_date"] = start_date.format("YYYY-MM-DDTHH:mm:ss[Z]")
        return config


@pytest.fixture(scope="session", name="abnormal_state")
def state_fixture():
    with open("integration_tests/abnormal_state.json", "r") as state_file:
        return json.load(state_file)
