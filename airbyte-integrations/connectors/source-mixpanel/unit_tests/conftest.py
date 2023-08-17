#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest


@pytest.fixture
def start_date():
    return pendulum.parse("2017-01-25").date()


@pytest.fixture
def config(start_date):
    return {
        "api_secret": "unexisting-secret",
        "attribution_window": 5,
        "project_timezone": pendulum.timezone("UTC"),
        "select_properties_by_default": True,
        "start_date": start_date,
        "end_date": start_date.add(days=31),
        "region": "US",
    }


@pytest.fixture
def config_raw(config):
    return {
        **config,
        "project_timezone": config["project_timezone"].name,
        "start_date": str(config["start_date"]),
        "end_date": str(config["end_date"]),
    }


@pytest.fixture(autouse=True)
def patch_time(mocker):
    mocker.patch("time.sleep")


@pytest.fixture(autouse=True)
def disable_cache(mocker):
    mocker.patch(
        "source_mixpanel.streams.cohorts.Cohorts.use_cache",
        new_callable=mocker.PropertyMock,
        return_value=False
    )
