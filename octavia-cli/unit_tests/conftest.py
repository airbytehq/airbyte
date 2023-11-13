#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture
def mock_api_client(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_telemetry_client(mocker):
    return mocker.Mock()
