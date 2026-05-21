#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest


pytest_plugins = ("connector_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    yield


def test_hyd39_with_creds_path_must_remain_blocking():
    pytest.fail("HYD39 intentional integration failure - with-creds path")
