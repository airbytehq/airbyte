#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import freezegun
import pytest


@pytest.fixture()
def mock_sleep(monkeypatch):
    with freezegun.freeze_time(datetime.datetime.now(), ignore=["_pytest.runner", "_pytest.terminal"]) as frozen_datetime:
        monkeypatch.setattr("time.sleep", lambda x: frozen_datetime.tick(x))
        yield


def pytest_addoption(parser):
    parser.addoption(
        "--skipslow", action="store_true", default=False, help="skip slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--skipslow"):
        skip_slow = pytest.mark.skip(reason="--skipslow option has been provided and this test is marked as slow")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
