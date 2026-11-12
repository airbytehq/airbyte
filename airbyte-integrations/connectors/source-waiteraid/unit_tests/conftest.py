# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Iterator

import pytest

from airbyte_cdk.test.mock_http import HttpMocker


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker
