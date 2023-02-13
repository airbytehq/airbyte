#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest

pytest_plugins = ("connector_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    yield
