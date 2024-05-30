#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
from pathlib import Path

import pendulum
import pytest


@pytest.fixture
def start_date():
    return pendulum.parse("2024-01-25T00:00:00").date()


@pytest.fixture
def config(start_date):
    return {
        "credentials": {"api_secret": "unexisting-secret"},
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


ENV_REQUEST_CACHE_PATH = "REQUEST_CACHE_PATH"
os.environ["REQUEST_CACHE_PATH"] = ENV_REQUEST_CACHE_PATH

def delete_cache_files(cache_directory):
    directory_path = Path(cache_directory)
    if directory_path.exists() and directory_path.is_dir():
        for file_path in directory_path.glob("*.sqlite"):
            file_path.unlink()

@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    # The problem: Once the first request is cached, we will keep getting the cached result no matter what setup we prepared for a particular test.
    # Solution: We must delete the cache before each test because for the same URL, we want to define multiple responses and status codes.
    delete_cache_files(os.getenv(ENV_REQUEST_CACHE_PATH))
    yield
