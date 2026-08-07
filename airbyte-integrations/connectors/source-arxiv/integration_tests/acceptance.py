#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest


pytest_plugins = ("connector_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance tests might require."""
    yield
