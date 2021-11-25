#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest

from .acceptance import minio_setup


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    yield from minio_setup()
