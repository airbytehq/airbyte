#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import pytest


pytest_plugins = ("connector_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    yield


def test_hyd39_no_creds_path_blocks_only_when_policy_is_wrong():
    pytest.fail("HYD39 intentional integration failure - no-creds path")
