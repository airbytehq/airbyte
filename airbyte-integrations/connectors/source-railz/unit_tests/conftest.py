# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock

# Include Airbyte's test utilities
pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

# Define a requests_mock fixture
@pytest.fixture
def requests_mock_fixture():
    with requests_mock.Mocker() as mock:
        yield mock
