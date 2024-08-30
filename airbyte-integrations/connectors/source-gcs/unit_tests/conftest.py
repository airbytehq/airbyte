# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging

import pytest


@pytest.fixture
def logger():
    return logging.getLogger("airbyte")
