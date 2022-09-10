#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta

import pendulum
import pytest


@pytest.fixture
def start_date():
    return pendulum.parse("2017-01-25T00:00:00Z").date()


@pytest.fixture
def config(start_date):
    return {
        "api_secret": "unexisting-secret",
        "attribution_window": 5,
        "project_timezone": pendulum.timezone("UTC"),
        "select_properties_by_default": True,
        "start_date": start_date,
        "end_date": start_date + timedelta(days=31),
        "region": "US",
    }


@pytest.fixture
def config_raw(config):
    config = {**config}
    config["project_timezone"] = config["project_timezone"].name
    config["start_date"] = "2017-01-25T00:00:00Z"
    config["end_date"] = "2017-02-25T00:00:00Z"
    return config
