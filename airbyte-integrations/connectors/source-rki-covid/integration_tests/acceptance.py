#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    yield
