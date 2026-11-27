# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Iterator

import pytest
from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker


@pytest.fixture(autouse=True)
def frozen_time() -> Iterator[None]:
    with freeze_time("2024-01-10T00:00:00Z"):
        yield


@pytest.fixture(params=["search", "top_headlines"])
def stream_name(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker
