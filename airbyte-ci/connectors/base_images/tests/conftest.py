#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"
