# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import random
import string

import pytest


@pytest.fixture
def random_string():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
