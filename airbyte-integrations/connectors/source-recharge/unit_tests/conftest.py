# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping
from unittest.mock import patch

import pytest


@pytest.fixture(name="config")
def config() -> Mapping[str, Any]:
    return {
        "authenticator": None,
        "access_token": "access_token",
        "start_date": "2021-08-15T00:00:00Z",
    }


@pytest.fixture(name="logger_mock")
def logger_mock_fixture() -> None:
    return patch("source_recharge.source.AirbyteLogger")
